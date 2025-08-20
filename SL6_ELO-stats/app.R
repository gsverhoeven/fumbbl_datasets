# I. Loading package and data ----
# Load packages
library(shiny)
library(dplyr)
library(reactable)
library(ggplot2)



# Load data
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
  titlePanel("Super League ELO Dashboard"),
  
  mainPanel(
    fluidRow(
      column(
        width = 5,
        selectInput("division", "Select Division:",
                                     choices = NULL),  # filled in server
      ),
      column(
        width = 7,
        (textOutput("division_title")),
        uiOutput("division_summary"),
        reactableOutput("division_table"),
        hr()
      )
    ),
    fluidRow(
      column(
        width = 5,
        selectInput("elo_type", "Select ELO Type for Chart:",
                                    choices = c("Race ELO" = "ranking",
                                                "Best ELO" = "best_ranking",
                                                "Global ELO" = "Coach.rating"),
                                    selected = "ranking")
      ),
      column(
        width = 7,
        h3(textOutput("elo_title")),
        plotOutput("elo_plot", height = "600px")
      )
    )
  )
)
  
  # sidebarLayout(
  #   sidebarPanel(
  #     selectInput("division", "Select Division:",
  #                 choices = NULL),  # filled in server
  #     
  #     selectInput("elo_type", "Select ELO Type for Chart:",
  #                 choices = c("Race ELO" = "ranking",
  #                             "Best ELO" = "best_ranking",
  #                             "Global ELO" = "Coach.rating"),
  #                 selected = "ranking")
  #   ),
  #   
  #   mainPanel(
  #     h3(textOutput("division_title")),
  #     uiOutput("division_summary"),
  #     reactableOutput("division_table"),
  #     hr(),
  #     h3(textOutput("elo_title")),
  #     plotOutput("elo_plot", height = "600px")
  #   )
  # )
# )


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
    paste("Distribution of", label, "per Division")
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
      )
    )
  })
  
  # ELO distribution plot
  output$elo_plot <- renderPlot({
    req(input$elo_type)
    
    ggplot(df_ELO_for_played_race_per_coach,
           aes(x = reorder(tournament_label, order),
               y = .data[[input$elo_type]])) +
      geom_jitter(alpha = 0.5, width = 0.2, color = "steelblue") +
      geom_boxplot(alpha = 0.2, outlier.shape = NA) +
      labs(
        x = "Tournament Division",
        y = names(which(c(ranking = "Race ELO",
                          best_ranking = "Best ELO",
                          `Coach.rating` = "Global ELO") == input$elo_type)),
        title = paste("Distribution of",  
                      switch(input$elo_type,
                                                 "ranking" = "Race ELO",
                                                 "best_ranking" = "Best ELO",
                                                 "Coach.rating" = "Global ELO"), 
                      "across Divisions")
      ) +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
  })
}

shinyApp(ui, server)
