#!/usr/bin/env Rscript
#' Parse RWT131 filtered peak areas and extract AdipoRon clearance data.
#'
#' Reads from the RWT131 output, writes a tidy TSV to data/.

root <- here::here()
source_path <- file.path(
  Sys.getenv("HOME"),
  "projects",
  "openadmet",
  "notebooks",
  "20251211_RWT131_CYP3A4_clearance_pilot_3",
  "output",
  "filtered_peak_areas.tsv"
)
out_path <- file.path(root, "data", "clearance_snippet.tsv")

df <- readr::read_delim(source_path)

out <- df |>
  dplyr::filter(
    drug %in% c("AdipoRon", "Eletriptan"),
    condition == "plus_NADP_plus_G6P_plus_G6PD",
    !exclude_wells,
    !is.na(area),
    Plate == "Plate03"
  ) |>
  dplyr::filter(area > 0) |>
  dplyr::select(
    c(
      "ocnt_batch",
      "drug",
      "drug_M",
      "timepoint_min_designed",
      "elapsed_time",
      "area",
      "well",
      "Plate"
    )
  )

write.table(out, out_path, sep = "\t", row.names = FALSE, quote = FALSE)
message(sprintf(
  "clearance_snippet.tsv: %s rows",
  format(nrow(out), big.mark = ",")
))
