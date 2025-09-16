# package uses outdated webshot, here we use webshot2

# Note: webshot uses PhantomJS, which is a headless browser that stopped development in 2018. Please use webshot2, which uses Chromium-based browsers.

# results in error: Error in tools::file_ext(output) == "png" && tools::file_ext(input) !=  : 
#'length = 8' in coercion to 'logical(1)': fixed using https://github.com/kcuilla/reactablefmtr/pull/59/commits/99cf8129c8975ec404a995d0d44a15d096fda603


save_reactable <- function(input,
                           output,
                           ...) {
  
  if (typeof(input) != "character" && attr(input, "class")[1] != "reactable" || typeof(input) != "character" && is.null(attr(input, "class")[1])) {
    
    stop("input must be either a reactable table, .html file, or .Rmd file")
  }
  
  '%notin%' <- Negate('%in%')
  
  if (typeof(input) == "character" && tools::file_ext(input) %notin% c("html", "Rmd") == TRUE) {
    
    stop("input must be either a reactable table, .html file, or .Rmd file")
  }
  
  if (tools::file_ext(output) %notin% c("png", "html") == TRUE) {
    
    stop("output must be either a .png or .html file")
  }
  
  if (tools::file_ext(output) == "html") {
    
    htmlwidgets::saveWidget(widget = input, file = output, selfcontained = TRUE)
    
    message("html file saved to ", getwd(), "/", output)
    
  } else if (tools::file_ext(output) == "png" && all(tools::file_ext(input) != "Rmd") && all(tools::file_ext(input) != "html")) {
    
    temp_html <- tempfile(
      pattern = tools::file_path_sans_ext(basename(output)),
      fileext = ".html")
    
    htmlwidgets::saveWidget(widget = input, file = temp_html, selfcontained = TRUE)
    
    webshot2::webshot(url = temp_html,
                      file = output,
                      zoom = 2,
                      delay = 1,
                      ...)
    
    invisible(file.remove(temp_html))
    
    message("image saved to ", getwd(), "/", output)
    
  } else if (tools::file_ext(input) == "Rmd") {
    
    message("Knitting R Markdown document...")
    
    webshot2::rmdshot(doc = input,
                      file = output,
                      zoom = 2,
                      delay = 1,
                      ...)
    
    message("image saved to ", getwd(), "/", output)
    
  } else if (tools::file_ext(input) == "html" && tools::file_ext(output) == "png") {
    
    webshot2::webshot(url = input,
                      file = output,
                      zoom = 2,
                      delay = 1,
                      ...)
    
    message("image saved to ", getwd(), "/", output)
    
  } else stop("please make sure input is either a reactable table, .html file, or .Rmd file,
              and output is either a .png or .html file")
  
}
