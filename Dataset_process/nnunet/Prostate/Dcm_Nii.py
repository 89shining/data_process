from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pydicom
import SimpleITK as sitk
from matplotlib.path import Path as MplPath


RAW_ROOT = Path(r"D:\WUSI\Prostate\Rawdata")
OUT_ROOT = Path(r"D:\WUSI\Prostate\datanii")
MAPPING_CSV = RAW_ROOT / "patient_mapping.csv"
SKIP_COMPLETE = True

INSTITUTIONS = [
    ("BJCH", "Postoperative_RT_BJCH", 0),
    ("FH", "Postoperative_RT_FH", 50),
]

ROI_ALIASES = {
    "ctv1": "CTV1",
    "ctv_high": "CTV1",
    "ctvhigh": "CTV1",
    "ctv2": "CTV2",
    "ctv": "CTV2",
}


def read_header(dicom_path: Path, tags: list[str] | None = None):
    return pydicom.dcmread(
        str(dicom_path),
        force=True,
        stop_before_pixels=True,
        specific_tags=tags,
    )


def canonical_roi_name(name: str) -> str | None:
    return ROI_ALIASES.get(name.strip().casefold())


def collect_dicom_files(patient_dir: Path) -> tuple[list[Path], list[Path]]:
    ct_by_series: dict[str, list[Path]] = {}
    rtstructs: list[Path] = []

    for dicom_path in patient_dir.rglob("*.dcm"):
        try:
            ds = read_header(
                dicom_path,
                ["Modality", "SeriesInstanceUID", "ImagePositionPatient", "InstanceNumber"],
            )
        except Exception:
            continue

        modality = getattr(ds, "Modality", None)
        if modality == "RTSTRUCT":
            rtstructs.append(dicom_path)
        elif modality == "CT":
            series_uid = str(getattr(ds, "SeriesInstanceUID", "NO_SERIES_UID"))
            ct_by_series.setdefault(series_uid, []).append(dicom_path)

    if not ct_by_series:
        raise RuntimeError(f"No CT DICOM files found in {patient_dir}")
    if not rtstructs:
        raise RuntimeError(f"No RTSTRUCT found in {patient_dir}")

    ct_files = max(ct_by_series.values(), key=len)
    return sort_ct_files(ct_files), sorted(rtstructs)


def sort_ct_files(ct_files: list[Path]) -> list[Path]:
    headers = []
    for dicom_path in ct_files:
        ds = read_header(
            dicom_path,
            ["ImagePositionPatient", "ImageOrientationPatient", "InstanceNumber"],
        )
        ipp = getattr(ds, "ImagePositionPatient", None)
        iop = getattr(ds, "ImageOrientationPatient", None)
        instance = int(getattr(ds, "InstanceNumber", 0))
        headers.append((dicom_path, ipp, iop, instance))

    first_iop = headers[0][2]
    if first_iop is not None:
        row = np.asarray([float(v) for v in first_iop[:3]])
        col = np.asarray([float(v) for v in first_iop[3:]])
        normal = np.cross(row, col)

        def position_key(item):
            dicom_path, ipp, _iop, instance = item
            if ipp is None:
                return float(instance)
            return float(np.dot(np.asarray([float(v) for v in ipp]), normal))

        return [item[0] for item in sorted(headers, key=position_key)]

    return [item[0] for item in sorted(headers, key=lambda item: item[3])]


def read_ct_image(ct_files: list[Path]) -> sitk.Image:
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames([str(p) for p in ct_files])
    return reader.Execute()


def find_rtstruct_with_targets(rtstructs: list[Path]) -> Path:
    fallback = rtstructs[0]
    for rt_path in rtstructs:
        ds = pydicom.dcmread(str(rt_path), force=True, stop_before_pixels=True)
        names = [str(roi.ROIName) for roi in getattr(ds, "StructureSetROISequence", [])]
        canonical = {canonical_roi_name(name) for name in names}
        if {"CTV1", "CTV2"}.issubset(canonical):
            return rt_path
    return fallback


def get_target_roi_numbers(rt_path: Path) -> dict[int, str]:
    ds = pydicom.dcmread(str(rt_path), force=True, stop_before_pixels=True)
    roi_numbers: dict[int, str] = {}
    for roi in getattr(ds, "StructureSetROISequence", []):
        canonical = canonical_roi_name(str(roi.ROIName))
        if canonical:
            roi_numbers[int(roi.ROINumber)] = canonical

    found = set(roi_numbers.values())
    missing = {"CTV1", "CTV2"} - found
    if missing:
        raise RuntimeError(f"{rt_path} missing target ROI(s): {sorted(missing)}")
    return roi_numbers


def contour_to_indices(image: sitk.Image, contour_data) -> np.ndarray:
    values = [float(v) for v in contour_data]
    points = np.asarray(values, dtype=np.float64).reshape(-1, 3)
    indices = [image.TransformPhysicalPointToContinuousIndex(tuple(p)) for p in points]
    return np.asarray(indices, dtype=np.float64)


def fill_polygon(mask: np.ndarray, polygon_xy: np.ndarray, z_index: int) -> None:
    depth, height, width = mask.shape
    if z_index < 0 or z_index >= depth or polygon_xy.shape[0] < 3:
        return

    min_x = max(int(np.floor(np.min(polygon_xy[:, 0]))), 0)
    max_x = min(int(np.ceil(np.max(polygon_xy[:, 0]))), width - 1)
    min_y = max(int(np.floor(np.min(polygon_xy[:, 1]))), 0)
    max_y = min(int(np.ceil(np.max(polygon_xy[:, 1]))), height - 1)
    if min_x > max_x or min_y > max_y:
        return

    xs = np.arange(min_x, max_x + 1)
    ys = np.arange(min_y, max_y + 1)
    grid_x, grid_y = np.meshgrid(xs, ys)
    points = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    inside = MplPath(polygon_xy).contains_points(points, radius=1e-6)
    mask[z_index, min_y : max_y + 1, min_x : max_x + 1] |= inside.reshape(len(ys), len(xs))


def rtstruct_to_masks(rt_path: Path, image: sitk.Image) -> tuple[np.ndarray, np.ndarray]:
    ds = pydicom.dcmread(str(rt_path), force=True)
    roi_numbers = get_target_roi_numbers(rt_path)
    shape = sitk.GetArrayFromImage(image).shape
    masks = {
        "CTV1": np.zeros(shape, dtype=bool),
        "CTV2": np.zeros(shape, dtype=bool),
    }

    for roi_contour in getattr(ds, "ROIContourSequence", []):
        roi_name = roi_numbers.get(int(getattr(roi_contour, "ReferencedROINumber", -1)))
        if roi_name not in masks:
            continue

        for contour in getattr(roi_contour, "ContourSequence", []):
            if not hasattr(contour, "ContourData"):
                continue
            ijk = contour_to_indices(image, contour.ContourData)
            z_index = int(round(float(np.mean(ijk[:, 2]))))
            polygon_xy = ijk[:, :2]
            fill_polygon(masks[roi_name], polygon_xy, z_index)

    return masks["CTV1"].astype(np.uint8), masks["CTV2"].astype(np.uint8)


def write_mask(mask_array: np.ndarray, reference_image: sitk.Image, out_path: Path) -> None:
    mask_image = sitk.GetImageFromArray(mask_array.astype(np.uint8))
    mask_image.CopyInformation(reference_image)
    sitk.WriteImage(mask_image, str(out_path))


def existing_output_is_complete(out_dir: Path) -> bool:
    paths = [out_dir / "image.nii.gz", out_dir / "CTV1.nii.gz", out_dir / "CTV2.nii.gz"]
    if not all(path.exists() for path in paths):
        return False

    try:
        image = sitk.ReadImage(str(paths[0]))
        ctv1 = sitk.ReadImage(str(paths[1]))
        ctv2 = sitk.ReadImage(str(paths[2]))
        if image.GetSize() != ctv1.GetSize() or image.GetSize() != ctv2.GetSize():
            return False
        if image.GetSpacing() != ctv1.GetSpacing() or image.GetSpacing() != ctv2.GetSpacing():
            return False
        if image.GetOrigin() != ctv1.GetOrigin() or image.GetOrigin() != ctv2.GetOrigin():
            return False
        if image.GetDirection() != ctv1.GetDirection() or image.GetDirection() != ctv2.GetDirection():
            return False
        return int(sitk.GetArrayFromImage(ctv1).sum()) > 0 and int(sitk.GetArrayFromImage(ctv2).sum()) > 0
    except Exception:
        return False


def convert_patient(patient_dir: Path, out_dir: Path) -> tuple[int, int]:
    ct_files, rtstructs = collect_dicom_files(patient_dir)
    rt_path = find_rtstruct_with_targets(rtstructs)

    candidates = []
    for candidate_ct_files in (ct_files, list(reversed(ct_files))):
        image = read_ct_image(candidate_ct_files)
        ctv1, ctv2 = rtstruct_to_masks(rt_path, image)
        candidates.append((int(ctv1.sum()), int(ctv2.sum()), image, ctv1, ctv2))

    candidates.sort(key=lambda item: (item[0] > 0 and item[1] > 0, item[0] + item[1]), reverse=True)
    ctv1_voxels, ctv2_voxels, image, ctv1, ctv2 = candidates[0]
    if ctv1_voxels == 0 or ctv2_voxels == 0:
        raise RuntimeError(f"Empty target mask after rasterization: CTV1={ctv1_voxels}, CTV2={ctv2_voxels}")

    out_dir.mkdir(parents=True, exist_ok=True)
    sitk.WriteImage(image, str(out_dir / "image.nii.gz"))
    write_mask(ctv1, image, out_dir / "CTV1.nii.gz")
    write_mask(ctv2, image, out_dir / "CTV2.nii.gz")
    return ctv1_voxels, ctv2_voxels


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    mapping_rows = []
    failures = []

    for institution_short, folder_name, start_index in INSTITUTIONS:
        institution_dir = RAW_ROOT / folder_name
        patient_dirs = sorted([p for p in institution_dir.iterdir() if p.is_dir()], key=lambda p: p.name)
        if len(patient_dirs) != 50:
            print(f"WARNING: {institution_dir} has {len(patient_dirs)} patient folders, expected 50", flush=True)

        for offset, patient_dir in enumerate(patient_dirs):
            p_id = f"p_{start_index + offset}"
            out_dir = OUT_ROOT / p_id
            mapping_rows.append(
                {
                    "p_id": p_id,
                    "institution": institution_short,
                    "original_patient_id": patient_dir.name,
                }
            )

            try:
                if SKIP_COMPLETE and existing_output_is_complete(out_dir):
                    print(f"{p_id} {institution_short} {patient_dir.name}: already complete, skipped", flush=True)
                    continue
                ctv1_voxels, ctv2_voxels = convert_patient(patient_dir, out_dir)
                print(
                    f"{p_id} {institution_short} {patient_dir.name}: "
                    f"CTV1={ctv1_voxels} voxels, CTV2={ctv2_voxels} voxels",
                    flush=True,
                )
            except Exception as exc:
                failures.append((p_id, institution_short, patient_dir.name, repr(exc)))
                print(f"ERROR {p_id} {institution_short} {patient_dir.name}: {exc}", flush=True)

    with MAPPING_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["p_id", "institution", "original_patient_id"])
        writer.writeheader()
        writer.writerows(mapping_rows)

    print(f"Wrote mapping: {MAPPING_CSV}", flush=True)
    print(f"Wrote NIfTI folders: {OUT_ROOT}", flush=True)
    if failures:
        print("Failures:")
        for failure in failures:
            print("\t".join(failure))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
