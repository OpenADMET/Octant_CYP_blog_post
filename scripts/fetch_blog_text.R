#!/usr/bin/env Rscript
# Download blog post from Google Docs as HTML (preserves hyperlinks)

library(googledrive)
library(here)

here::i_am("scripts/fetch_blog_text.R")

drive_auth(cache = "~/.secrets")

doc_id <- as_id("1m6I11d93iwLTR8LS7BytU9zliY5CtnculsUsuHzxGBE")
out_path <- here("data", "raw", "blog_post_text.html")

# fetch metadata for revision timestamp
meta <- drive_get(doc_id)
modified <- meta$drive_resource[[1]]$modifiedTime
message("Google Doc last modified: ", modified)

drive_download(
  file = doc_id,
  path = out_path,
  type = "text/html",
  overwrite = TRUE
)

# write revision timestamp alongside the text
writeLines(modified, here("data", "raw", "blog_post_revision.txt"))

message("Saved to: ", out_path)
message("Revision timestamp: ", modified)
