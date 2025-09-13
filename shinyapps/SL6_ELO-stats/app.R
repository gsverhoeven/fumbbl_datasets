# I. Loading package and data ----
# Load packages
library(shiny)
library(dplyr)
library(reactable)
library(ggplot2)
library(plotly)


# Info to update manually at this stage
global_ELO_last_update <- as.Date("20/08/2025", "%d/%m/%Y")
NAF_ELO_last_update <- as.Date("19/08/2025", "%d/%m/%Y")

# Load data (data are created by create_plots.Rmd)
df_ELO_for_played_race_per_coach <- read.csv(file ="ELO_for_played_race_per_coach.csv")


# Calculate % of coaches without ranking data
df_labels <- df_ELO_for_played_race_per_coach %>%
  group_by(tournament_name, order) %>%
  summarise(
    total = n(),
    valid = sum(if_any(c(`ranking`, `best_ranking`, `Coach.rating`), ~ !is.na(.))),
    .groups = "drop"
  ) %>%
  mutate(share = 100 * valid / total,
         tournament_label = paste0(tournament_name, " (", round(share, 1), "%)"))

# Merge with the main dataset
df_ELO_for_played_race_per_coach <- df_ELO_for_played_race_per_coach %>%
  left_join(df_labels %>% select(tournament_name, tournament_label),
            by = "tournament_name")

# User interface
ui <- fluidPage(
  # CSS Style
  # Put the "summary" tag in underlined blue, to highlight it can be clicked.
  tags$head(
    tags$style(HTML("
    details > summary {
      cursor: pointer;
      color: #0073e6;
      font-weight: bold;
      text-decoration: underline;
      margin-top: 10px;
    }
    details > summary:hover {
      color: #005bb5;
    }
    details {
      margin-bottom: 15px;
      font-style: italic;
    }
  "))
  ),
  
  
  titlePanel("Super League - Season 6 - ELO Dashboard"),
  
  mainPanel(
    fluidRow(
      column(
        width = 4,
        selectInput("division", "Select Division:",
                                     choices = NULL),  # filled in server
      ),
      column(
        width = 8,
        tags$details(
          tags$summary(HTML(sprintf("<b>How to understand ELO (click to expand)</b>"))),
          p("In short, a higher ELO means a stronger coach."),
          p("A difference of 10 in ELO means 54% chance of victory for the stronger coach, a difference of 50 means 68%."),
          HTML(sprintf("<p>See <a href='https://www.thenaf.net/tournaments/rankings/elo-ranking/'>details</a> on how ELO are calculated by the NAF.</p>")),
          p("3 types of ELO are displayed on this page:"),
          HTML(sprintf("<p><b>Race ELO</b> (last update: %s): the NAF ELO score of the coach for the race played for the Super League</p>", NAF_ELO_last_update)),
          HTML(sprintf("<p><b>Best ELO</b> (last update: %s): the best NAF ELO score of the coach across all the races they ever played</p>", NAF_ELO_last_update)),
          HTML(sprintf("<p><b>Global ELO</b> (last update: %s): an ELO score calculated with the same formula as the one used by the NAF but including all matches, irrespective of races played (so being good at more than one race increases further the ELO score for instance). Comes from <a href='https://bloodbowl.dk/coach-rating/'>https://bloodbowl.dk/coach-rating/</a></p>", global_ELO_last_update)),
        ),
        br(),
        (textOutput("division_title")),
        uiOutput("division_summary"),
        reactableOutput("division_table"),
        hr()
      )
    ),
    fluidRow(
      column(
        width = 4,
        selectInput("elo_type", "Select ELO Type for Chart:",
                                    choices = c("Race ELO" = "ranking",
                                                "Best ELO" = "best_ranking",
                                                "Global ELO" = "Coach.rating"),
                                    selected = "ranking")
      ),
      column(
        width = 8,
        
        tags$details(
          tags$summary(HTML(sprintf("<b>How to read boxplots (click to expand)</b>"))),
          p("The charts show how ELO scores are distributed across coaches per tournament/division:"),
          tags$ul(
            tags$li("The dashed line inside the box is the mean (average), , gives the overall central value, which can be shifted by extreme cases."),
            tags$li("The thick line inside the box is the median (half the values are above, half below). For most divisions, that more or less shows the minimum level required to stay within the division (since half of coaches are relegated)."),
            tags$li("The bottom and top of the box show the first (Q1) and third (Q3) quartiles — together they cover the middle 50% of the data. So basically the Q3 is the lower bound of the level of most players."),
            tags$li("The 'whiskers' (lines extending from the box) show the range of most values."),
            tags$li("Points outside the whiskers (if shown) are unusually high or low values (outliers)."),
            tags$li("The % in brackets after the name of each tournament / division are the % of coaches with links to their NAF profile on Fumbbl.")
          )
        ),
        br(),
        h3(textOutput("elo_title")),
        plotlyOutput("elo_plot", height = "600px"),
        plotlyOutput("elo_plot_per_division", height = "600px")
      )
    )
  )
)


server <- function(input, output, session) {
  
  # Populate dropdown for divisions in order
  observe({
    divs <- df_ELO_for_played_race_per_coach %>%
      distinct(tournament_name, order) %>%
      arrange(order)
    updateSelectInput(session, "division",
                      choices = setNames(divs$tournament_name, divs$tournament_name),
                      selected = divs$tournament_name[1])
  })
  
  # Compute division summary
  division_summary_data <- reactive({
    req(input$division)
    df <- df_ELO_for_played_race_per_coach %>%
      filter(tournament_name == input$division)
    
    df %>%
      summarise(
        avg_ranking = mean(ranking, na.rm = TRUE),
        avg_best    = mean(best_ranking, na.rm = TRUE),
        avg_global  = mean(Coach.rating, na.rm = TRUE)
      )
  })
  
  # Title
  output$division_title <- renderText({
    paste("Division:", input$division)
  })
  
  output$elo_title <- renderText({
    label <- switch(input$elo_type,
                    "ranking" = "Race ELO",
                    "best_ranking" = "Best ELO",
                    "Coach.rating" = "Global ELO")
    paste("Distribution of", label )
  })
  
  # Summary line
  output$division_summary <- renderText({
    s <- division_summary_data()
    HTML(sprintf("<b>Average Race ELO:</b> %.1f | <b>Average Best ELO:</b> %.1f | <b>Average Global ELO:</b> %.1f",
                 s$avg_ranking, s$avg_best, s$avg_global))
  })
  
  # Table per division
  output$division_table <- renderReactable({
    req(input$division)
    df <- df_ELO_for_played_race_per_coach %>%
      filter(tournament_name == input$division) %>%
      group_by(coach_name) %>%
      rename("Coach name"   = coach_name) %>% 
      summarise(
        `Race ELO`   = mean(ranking, na.rm = TRUE),
        `Best ELO`   = max(best_ranking, na.rm = TRUE),
        `Global ELO` = mean(Coach.rating, na.rm = TRUE),
        .groups = "drop"
      )
    
    reactable(
      df,
      defaultSorted = list("Global ELO" = "desc"),
      striped = TRUE,
      filterable = TRUE,
      highlight = TRUE,
      defaultPageSize = 20,
      columns = list(
        `Race ELO`   = colDef(format = colFormat(digits = 1)),
        `Best ELO`   = colDef(format = colFormat(digits = 1)),
        `Global ELO` = colDef(format = colFormat(digits = 1))
      ),
      theme = reactableTheme(
        stripedColor = "darkgrey" 
      )
    )
  })
  
  # ELO distribution plot per tournament
  output$elo_plot <- renderPlotly({
    req(input$elo_type)
    
    plot_ly(
      df_ELO_for_played_race_per_coach,
      x = ~reorder(tournament_label, order),
      y = ~.data[[input$elo_type]],
      type = "scatter",
      showlegend = FALSE,       # hides it from the legend
      boxpoints = "all",   # shows jittered points
      jitter = 0.2,
      pointpos = 0,
      marker = list(size = 6, opacity = 0.3),
      text = ~paste(
        "Coach:", coach_name,
        "<br>Race ELO:", round(ranking,1),
        "<br>Best ELO:", round(best_ranking,1),
        "<br>Global ELO:", round(Coach.rating,1)
      ),
      hoverinfo = "text",
      boxmean = TRUE # Add the mean
    ) %>% 
      layout(
        xaxis = list(title = "Tournament"),
        yaxis = list(title = switch(input$elo_type,
                                    "ranking" = "Race ELO",
                                    "best_ranking" = "Best ELO",
                                    "Coach.rating" = "Global ELO"))
      ) %>% 
      add_trace(
        type = "box",
        boxpoints = FALSE,   # no points
        hoverinfo = "y",     # will display Q1, median, Q3
        line = list(color = "lightgray"),
        fillcolor = "white"
      )
  })
  
  # ELO distribution plot per division
  output$elo_plot_per_division <- renderPlotly({
    req(input$elo_type)
    
    plot_ly(
      df_ELO_for_played_race_per_coach,
      x = ~division,
      y = ~.data[[input$elo_type]],
      type = "scatter",
      showlegend = FALSE,       # hides it from the legend
      boxpoints = "all",   # shows jittered points
      jitter = 0.2,
      pointpos = 0,
      marker = list(size = 6, opacity = 0.3),
      text = ~paste(
        "Coach:", coach_name,
        "<br>Race ELO:", round(ranking,1),
        "<br>Best ELO:", round(best_ranking,1),
        "<br>Global ELO:", round(Coach.rating,1)
      ),
      hoverinfo = "text",
      boxmean = TRUE # Add the mean
    ) %>% 
      layout(
        xaxis = list(title = "Division"),
        yaxis = list(title = switch(input$elo_type,
                                    "ranking" = "Race ELO",
                                    "best_ranking" = "Best ELO",
                                    "Coach.rating" = "Global ELO"))
      ) %>% 
      add_trace(
        type = "box",
        boxpoints = FALSE,   # no points
        hoverinfo = "y",     # will display Q1, median, Q3
        line = list(color = "lightgray"),
        fillcolor = "white"
      )
  })
}

shinyApp(ui, server)
