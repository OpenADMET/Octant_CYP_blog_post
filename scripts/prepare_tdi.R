#!/usr/bin/env Rscript
#' Parse LMO-27 pIC50 comparison RDS and write a tidy TSV for figure 7B.
#'
#' Reads from data/rds/, writes to data/.

root <- here::here()
rds_path <- file.path(root, "data", "rds",
                      "LMO-27.pIC50_comparisons_dist-12pt.RDS")
out_path <- file.path(root, "data", "tdi_pic50_shift.tsv")

comp <- readRDS(rds_path)

out <- data.frame(
  drug       = comp$drug,
  delta_mean = comp$mean,
  delta_sd   = comp$sd,
  delta_q2.5 = comp$q2.5,
  delta_q97.5 = comp$q97.5
)

write.table(out, out_path, sep = "\t", row.names = FALSE, quote = FALSE)
message(sprintf("tdi_pic50_shift.tsv: %s rows", format(nrow(out), big.mark = ",")))

# --- DRC curves + points for ALL drugs (not just troleandomycin) ---
fits_path <- file.path(root, "data", "rds",
                       "LMO-27.pIC50_fits_regen_12pt.RDS")
fits <- readRDS(fits_path)
all_drugs <- fits[fits$drug != "vehicle_only", ]

# Fitted curves
curves_out <- do.call(rbind, lapply(seq_len(nrow(all_drugs)), function(i) {
  cv <- all_drugs$curves[[i]]
  cv$drug <- all_drugs$drug[i]
  cv$preincubation <- all_drugs$NADP_preincubation[i]
  cv$norm_value <- (cv$value - cv$emax) / (cv$emin - cv$emax)
  cv[, c("drug", "log10_drug_M", "norm_value", "preincubation")]
}))
write.table(curves_out, file.path(root, "data", "tdi_drc_curves.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)

# Raw points
pts_out <- do.call(rbind, lapply(seq_len(nrow(all_drugs)), function(i) {
  pt <- all_drugs$points[[i]]
  pt$drug <- all_drugs$drug[i]
  pt$preincubation <- all_drugs$NADP_preincubation[i]
  pt$norm_value <- (pt$value - pt$emaxf) / (pt$eminf - pt$emaxf)
  pt[, c("drug", "log10_conc", "norm_value", "preincubation")]
}))
write.table(pts_out, file.path(root, "data", "tdi_drc_points.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)

# DRC fit parameters (pIC50, hillslope, IC50 per drug × condition)
params_out <- fits[fits$drug != "vehicle_only",
  c("drug", "NADP_preincubation", "estimate_pIC50", "estimate_hillslope",
    "Q2.5_pIC50", "Q97.5_pIC50", "IC50_M", "IC50_label")]
names(params_out)[names(params_out) == "NADP_preincubation"] <- "preincubation"
write.table(params_out, file.path(root, "data", "tdi_drc_params.tsv"),
            sep = "\t", row.names = FALSE, quote = FALSE)

message(sprintf("tdi_drc_curves.tsv: %s rows", nrow(curves_out)))
message(sprintf("tdi_drc_points.tsv: %s rows", nrow(pts_out)))
message(sprintf("tdi_drc_params.tsv: %s rows", nrow(params_out)))
