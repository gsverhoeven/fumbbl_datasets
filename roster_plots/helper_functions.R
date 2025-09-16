source("save_reactable.R")

build_table <- function(data, type, save) {
  data <- data %>% 
    adorn_totals("col") %>%
    adorn_totals("row") %>%
    # custom ordering
    arrange(
      case_when(Skill == "No skill" ~ 1,
                Skill == "Total" ~ 3,
                TRUE ~ 2),
      desc(Total)
    )
  
  # Round because save_reactable() otherwise messes up the formating of digits
  if (type == "percentage") {
    data <- data %>% mutate(across(where(is.numeric), ~ round(., 0)))
  } else {
    data <- data %>% mutate(across(where(is.numeric), ~ round(., 1)))
  }
  
  default_col_format <- if (type == "percentage") {
    colFormat(digits = 0, suffix = "%")
  } else if (type == "team") {
    colFormat(digits = 1) # no % suffix
  } else {
    colFormat() # fallback
  }
  
  table <- reactable(
    data %>% select(-Total), # select to remove for team_table (to be done)
    # searchable = TRUE,
    sortable = TRUE,
    # filterable = TRUE,
    striped = TRUE,
    highlight = TRUE,
    columns = list(
      Skill = colDef(align = "left"),  # no % suffix here
      format = colFormat(suffix = "") # does not work at this stage
    ),
    defaultColDef = colDef(           # <- not .default !
      align = "center",
      format = default_col_format
      
    ),
    defaultPageSize = 20,
    bordered = TRUE,
    rowStyle = function(index) {
      if (index == nrow(data)) {
        list(fontWeight = "bold")
      } else {
        NULL
      }
    },
    theme = reactableTheme(
      borderColor = "#e0e0e0",
      highlightColor = "#f0f8ff"
    )
  )
  
  if(save == TRUE) { 
    save_reactable(table, 
                   gsub(" ", "_", paste0(tournament_ruleset, "/", group_name, "_", type, "-stat_plot_", race_name, ".png")))
  }
  
  return(table)
}

make_skill_table <- function(roster_filter) {
  df <- df_rosters1 %>%
    filter(roster.name == roster_filter & position != "" & number != 99) %>%
    # Drop rows with no skill if at least one other skill is filled for the player (to solve a bug with multiple rows for some players with only 1 skill)
    group_by(player_id) %>%
    mutate(all_empty = all(name == "" | is.na(name))) %>%
    filter(
      # Case 1: all rows empty → keep only the first
      (all_empty & row_number() == 1) |
        # Case 2: otherwise → keep only non-empty rows
        (!all_empty & name != "")
    ) %>% 
    ungroup() %>% 
    mutate(name = ifelse(name == "", "No skill", name),
           team_count = n_distinct(team_id)) %>% 
    group_by(position) %>% 
    mutate(positional_count = n_distinct(player_id)) %>% 
    ungroup() %>% 
    group_by(position, name) %>%
    summarise(percentage_picks = 100*n() / first(positional_count),
              team_picks = n() / first(team_count),
              .groups = "drop") %>% 
    rename("Skill" = name)
  
  percentage_table <- df %>%
    select(-team_picks) %>% 
    pivot_wider(
      names_from = position,
      values_from = percentage_picks,
      values_fill = list(percentage_picks = 0)
    )
  
  team_table <- df %>%
    select(-percentage_picks) %>% 
    filter(Skill != "No skill") %>% 
    pivot_wider(
      names_from = position,
      values_from = team_picks,
      values_fill = list(team_picks = 0)
    )
  
  return(  tagList(
    build_table(percentage_table, "percentage", TRUE),
    build_table(team_table, "team", TRUE)
  ))
}
