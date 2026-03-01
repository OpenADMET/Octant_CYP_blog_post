#!/usr/bin/env Rscript
#' Parse the Will-It-Fly RDS file and write a sanitized TSV.
#'
#' Reads from data/rds/, writes to data/.

root <- here::here()
rds_path <- file.path(root, "data", "rds",
                      "Willitfly_NH4FvsAmFormate_comparison_df.rds")
out_path <- file.path(root, "data", "willitfly.tsv")

df <- readRDS(rds_path)

out <- data.frame(
  ocnt_batch = df$ocnt_name,
  ammonium_fluoride_area = df$AmF_area,
  ammonium_formate_area = df$AmFormate_area
)

write.table(out, out_path, sep = "\t", row.names = FALSE, quote = FALSE)
message(
  sprintf("willitfly.tsv: %s rows", format(nrow(out), big.mark = ","))
)
