cbpalette <- c(
  "#ffcc3d", # yellow-orange (light)
  "#163274", # darker blue (dark)
  "#f06a63", # red (lighter)
  "#58a787", # teal (mid-tone)
  "#d7433b", # red (brightest)
  "#008d98", # teal (darker)
  "#c3d878", # yellow (lighter)
  "#246893", # dark blue (mid-tone)
  "#c3a016", # yellow (brightest)
  "#ff8e5e", # orange (mid-tone)
  "#95caa6", # light green (lighter)
  "#8ebacd", # light blue (mid-tone)
  "#0c1f4b"  # darkest blue
)

cbpalette2 <- c(
  "#e69f00", # orange
  "#56b4e9", # sky-blue
  "#009e73", # bluish green
  "#d55e00", # vermillion
  "#cc79a7", # reddish purple
  "#0072b2", # blue
  "#b2df8a", # light green
  "#f0e442", # yellow
  "#33a02c", # darker green
  "#fb9a99", # pink
  "#1f78b4", # darker blue
  "#a6cee3", # light cyan
  "#999999"  # grey
)

theme_pub <- function(base_size = 11, base_family = "Arial") {
  theme_bw(base_size = base_size, base_family = base_family) +
    theme(
      panel.grid.minor.x = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.minor.y = element_blank(),
      panel.grid.major.y = element_line(
        colour = "#ECECEC",
        linewidth = 0.5,
        linetype = 1
      ),
      panel.background = element_blank(),
      axis.title.x = element_text(size = rel(1), vjust = 0.25),
      axis.title.y = element_text(size = rel(1), vjust = 0.35),
      axis.text.y = element_text(size = rel(1), color = "black"),
      axis.text.x = element_text(
        angle = 45,
        color = "black",
        hjust = 1,
        size = rel(1)
      ),
      legend.title = element_text(size = rel(1)),
      legend.key = element_rect(fill = "white"),
      legend.key.size = unit(0.02, "npc"),
      legend.text = element_text(size = rel(1)),
      strip.text = element_text(size = rel(1)),
      strip.background = element_blank(),
      plot.title = element_text(size = rel(1), hjust = 0.5),
      plot.subtitle = element_text(size = rel(0.8), hjust = 0)
    )
}
