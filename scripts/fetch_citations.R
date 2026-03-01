#!/usr/bin/env Rscript
# Fetch citation metadata from DOIs and cache in data/citations.tsv.
#
# Usage: Rscript scripts/fetch_citations.R [--refresh]
#
# Reads:  data/raw/blog_post_text.html  (to extract citation links)
# Writes: data/citations.tsv            (cached citation metadata)
#
# Non-DOI citations are written with empty metadata fields for manual editing.
# Existing manually edited entries are preserved unless --refresh is passed.

library(here)
library(xml2)
library(stringr)
library(httr)
library(jsonlite)

here::i_am("scripts/fetch_citations.R")

refresh <- "--refresh" %in% commandArgs(trailingOnly = TRUE)

# --- extract citation links from HTML -----------------------------------------

doc <- read_html(here("data", "raw", "blog_post_text.html"))
links <- xml_find_all(doc, "//a[@href]")

citations <- data.frame(
  number = character(),
  url = character(),
  doi = character(),
  stringsAsFactors = FALSE
)

for (l in links) {
  href <- xml_attr(l, "href")
  text <- trimws(xml_text(l))

  # only citation-style links (text is a number, possibly in brackets)
  if (!grepl("^\\[?\\d+\\]?$", text)) next

  # unwrap Google redirect URLs
  if (grepl("google.com/url", href)) {
    m <- str_match(href, "[?&]q=([^&]+)")
    if (!is.na(m[1, 2])) href <- URLdecode(m[1, 2])
  }

  num <- gsub("\\[|\\]", "", text)

  # extract DOI from URL (works for doi.org, pubs.acs.org/doi/..., etc.)
  doi_match <- str_extract(href, "10\\.\\d{4,}/[^\\s&]+")
  # clean trailing punctuation that may have been captured
  if (!is.na(doi_match)) {
    doi_match <- str_remove(doi_match, "[.)]+$")
  }

  citations <- rbind(citations, data.frame(
    number = num,
    url = href,
    doi = ifelse(is.na(doi_match), "", doi_match),
    stringsAsFactors = FALSE
  ))
}

# deduplicate by number
citations <- citations[!duplicated(citations$number), ]
citations <- citations[order(as.integer(citations$number)), ]

message("Found ", nrow(citations), " citations (",
        sum(citations$doi != ""), " with DOIs)")

# --- load existing cache ------------------------------------------------------

cache_path <- here("data", "citations.tsv")
cached <- if (file.exists(cache_path)) {
  read.delim(cache_path, stringsAsFactors = FALSE, na.strings = "")
} else {
  data.frame()
}

# --- fetch metadata from DOI API ----------------------------------------------

fetch_doi_metadata <- function(doi) {
  url <- paste0("https://doi.org/", doi)
  resp <- tryCatch(
    GET(url, add_headers(Accept = "application/citeproc+json"),
        timeout(10)),
    error = function(e) NULL
  )

  if (is.null(resp) || status_code(resp) != 200) {
    message("  Failed to fetch: ", doi)
    return(list(title = "", authors = "", journal = "", year = ""))
  }

  meta <- fromJSON(content(resp, as = "text", encoding = "UTF-8"),
                   simplifyVector = FALSE)

  # extract authors
  authors <- ""
  if (!is.null(meta$author)) {
    author_names <- vapply(meta$author, function(a) {
      paste0(a$family %||% "", ", ", substr(a$given %||% "", 1, 1), ".")
    }, character(1))
    if (length(author_names) > 3) {
      authors <- paste0(paste(author_names[1:3], collapse = "; "), " et al.")
    } else {
      authors <- paste(author_names, collapse = "; ")
    }
  }

  # extract year
  year <- ""
  if (!is.null(meta$issued$`date-parts`)) {
    year <- as.character(meta$issued$`date-parts`[[1]][[1]])
  }

  # extract journal
  journal <- meta$`container-title` %||% ""

  # extract journal — strip HTML entities
  journal <- gsub("&amp;", "&", journal)

  # extract title — strip HTML tags and normalize whitespace
  title <- meta$title %||% ""
  title <- gsub("<[^>]+>", "", title)
  title <- gsub("\\s+", " ", trimws(title))

  list(title = title, authors = authors, journal = journal, year = year)
}

# --- build output table -------------------------------------------------------

results <- data.frame(
  number = citations$number,
  url = citations$url,
  doi = citations$doi,
  title = character(nrow(citations)),
  authors = character(nrow(citations)),
  journal = character(nrow(citations)),
  year = character(nrow(citations)),
  tooltip = character(nrow(citations)),
  stringsAsFactors = FALSE
)

for (i in seq_len(nrow(results))) {
  num <- results$number[i]
  doi <- results$doi[i]

  # check if we already have cached data for this citation
  cached_row <- if (nrow(cached) > 0) cached[cached$number == num, ] else data.frame()

  if (nrow(cached_row) > 0 && !refresh &&
      !is.na(cached_row$title[1]) && cached_row$title[1] != "") {
    results$title[i] <- cached_row$title[1]
    results$authors[i] <- cached_row$authors[1]
    results$journal[i] <- cached_row$journal[1]
    results$year[i] <- cached_row$year[1]
    results$tooltip[i] <- cached_row$tooltip[1]
    message("[", num, "] cached: ", substr(cached_row$title[1], 1, 60))
    next
  }

  if (doi == "") {
    message("[", num, "] no DOI — fill in manually")
    next
  }

  message("[", num, "] fetching: ", doi)
  meta <- fetch_doi_metadata(doi)
  results$title[i] <- meta$title
  results$authors[i] <- meta$authors
  results$journal[i] <- meta$journal
  results$year[i] <- meta$year

  # build default tooltip: Authors (Year). Title. Journal.
  tooltip_parts <- character()
  if (meta$authors != "") tooltip_parts <- c(tooltip_parts, meta$authors)
  if (meta$year != "") tooltip_parts <- c(tooltip_parts, paste0("(", meta$year, ")."))
  if (meta$title != "") {
    # ensure title ends with a period
    t <- meta$title
    if (!grepl("[.!?]$", t)) t <- paste0(t, ".")
    tooltip_parts <- c(tooltip_parts, t)
  }
  if (meta$journal != "") {
    tooltip_parts <- c(tooltip_parts, paste0(meta$journal, "."))
  }
  results$tooltip[i] <- paste(tooltip_parts, collapse = " ")

  Sys.sleep(0.5)  # be polite to the API
}

# --- write output -------------------------------------------------------------

write.table(results, cache_path, sep = "\t", row.names = FALSE,
            quote = TRUE, na = "")
message("Wrote: ", cache_path)
