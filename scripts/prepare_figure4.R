#!/usr/bin/env Rscript
#' Parse figure 4 RDS files and write sanitized TSVs.
#'
#' Reads from data/rds/, writes to data/.

root <- here::here()

write_tsv <- function(df, path) {
  write.table(df, path, sep = "\t", row.names = FALSE, quote = FALSE)
  message(sprintf("%s: %s rows", basename(path), format(nrow(df), big.mark = ",")))
}

# --- RWT115: evaporation data (panel A) ---
rwt115 <- readRDS(file.path(root, "data", "rds", "RWT115_anno_data_df.RDS"))
rwt115_out <- data.frame(
  DMSO_percent   = rwt115$DMSO_percent,
  total_volume   = rwt115$total_volume,
  time_min       = rwt115$time_min,
  percent_volume = rwt115$percent_volume
)
write_tsv(rwt115_out, file.path(root, "data", "evaporation.tsv"))

# --- RWT92: phosphate buffer activity (panel B) ---
rwt92 <- readRDS(file.path(root, "data", "rds", "RWT92_norm_data.RDS"))
rwt92_out <- data.frame(
  empty_wells              = rwt92$empty_wells,
  matrix                   = rwt92$matrix,
  condition                = rwt92$condition,
  baculosome               = rwt92$baculosome,
  MgCl2_mM                 = rwt92$MgCl2_mM,
  buffer_ionic_strength_M  = rwt92$`buffer ionic strength (M)`,
  fc                       = rwt92$fc
)
write_tsv(rwt92_out, file.path(root, "data", "buffer_activity.tsv"))
