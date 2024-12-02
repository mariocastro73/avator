##------ mon 07 oct 2024 12:55:51 CET ------##
#
############## Libraries 
library(dplyr)
library(shape)
library(RColorBrewer)
library(MASS)
library(RTriangle)
library(readr)
library(deldir)
library(tripack)

############## Auxiliary functions 
# Takes a dataframe with coordinates x and y and compute all the metrics related to a Voronoi tesselation (distribution of neighbors and areas)
datavoronoi <- function(data,doplot=FALSE) {
  colnames(data) <- c('x','y') # Rename columns
  n <- length(data$x)
  p <- pslg(data)
  t <- triangulate(p)
  E <- t$E
  nn <-matrix(0,nrow=n,ncol=n)
  for(i in 1:dim(t$E)[1]) {
    nn[E[i,1],E[i,2]] = 1 
    nn[E[i,2],E[i,1]] = 1 
  }
  ind <- which(t$PB==0)
  neigh <- colSums(nn)[ind]
  # neigh <- neigh[neigh>4]
  r <- range(neigh)
  h <- hist(neigh,(r[1]-1):(r[2]),plot = doplot)
  aux <- table(neigh[neigh>4])
  p6 <- aux[names(aux)=="6"]/sum(aux)
  print(aux)
  # p6 <- h$density[which(h$breaks==6)-1]
  mu2 <- var(neigh)
  
  lem <- c(p6,mu2) # Store lemaitre coefficients (height of distribution at n=6 and variance of distribution)
  p61 <- seq(0.1,.7,.01) # Auxiliary vector for plotting 
  p62 <- seq(0.1,1,.01) # Auxiliary vector for plotting 
  mu2 <- seq(0,4,.01) # Auxiliary vector for plotting 
  
  output <- list(lem=lem,neigh=neigh,mu2=mu2,p61=p61,p62=p62,data=data,triangles=t,nn=nn) # Store data into list
  return(output)  # Return list
}

# Create a simple Lemaitre's plot
plotlemaitre <- function(output,add=FALSE,mycex=2,mypch=19,ymax=10,ymin=-0.9,defaultcol=rgb(red = 0, green = 0, blue = 1, alpha = 0.3)) {
  with(output,{
    if(add==FALSE) { # if add=TRUE, adds new data to current plot
      plot(p61,1/(2*pi*p61^2),type='l',xlab=expression(p[6])
           ,ylab=expression(mu[2]),ylim=c(ymin,ymax),xlim=c(0,1),lwd=4,bty='l',
           cex.lab=2,cex.axis=1.5,main="Lemaitre's plot",cex.main=2);
      lines(p62,1-p62,lty=2,lwd=4)  ;}
    points(lem[1],lem[2],pch=mypch,col=defaultcol,cex=mycex)} # True data
    # points(lem[1],lem[2],pch=mypch,col=1,bg=defaultcol,cex=mycex)} # True data
  )
}

# Function to generate a perfect triangular tessellation
generate_triangular_tessellation <- function(n_rows, n_cols, spacing = 1) {
  points <- data.frame(x = numeric(0), y = numeric(0))  # Empty dataframe to store coordinates
  
  for (row in 0:(n_rows - 1)) {
    for (col in 0:(n_cols - 1)) {
      # Calculate x and y coordinates
      x_coord <- col * spacing + (row %% 2) * (spacing / 2)  # Offset every other row
      y_coord <- row * (spacing * sqrt(3) / 2)  # Vertical spacing based on equilateral triangles
      
      # Add the coordinates to the dataframe
      points <- rbind(points, data.frame(x = x_coord, y = y_coord))
    }
  }
  
  return(points)
}


angle_distr <- function(df) {
  # Delaunay triangulation
  x <- df$x
  y <- df$y
  tri <- tri.mesh(x, y)
  
  # Extract triangles from the Delaunay triangulation
  triangles <- triangles(tri)  # This function extracts the triangle vertices
  # Uncomment the follwing lines if you want to analyze only the boundary triangles
  # boundary <- convex.hull(tri)$i
  # triangles <- triangles[which(!(triangles[,1] %in% boundary)
  #           & !(triangles[,2] %in% boundary)
  #           & !(triangles[,3] %in% boundary)) ,]
  # Initialize sum of angles
  total_order <- 0
  total_triangles <- nrow(triangles)
  to <- c()
  # Loop through each triangle
  for (i in 1:total_triangles) {
    # Get coordinates of the triangle vertices
    p1 <- c(x[triangles[i, 1]], y[triangles[i, 1]])
    p2 <- c(x[triangles[i, 2]], y[triangles[i, 2]])
    p3 <- c(x[triangles[i, 3]], y[triangles[i, 3]])
    
    # Calculate the distances between vertices
    d12 <- sqrt(sum((p1 - p2)^2))
    d23 <- sqrt(sum((p2 - p3)^2))
    d31 <- sqrt(sum((p3 - p1)^2))
    
    # Calculate the angles between the sides
    angle1 <- acos(.99*(d12^2 + d31^2 - d23^2) / (2 * d12 * d31))
    angle2 <- acos(.99*(d23^2 + d12^2 - d31^2) / (2 * d23 * d12))
    angle3 <- acos(.99*(d31^2 + d23^2 - d12^2) / (2 * d31 * d23))
    # cat(i,(d12^2 + d31^2 - d23^2) / (2 * d12 * d31),"\n")
    
    # The ideal angle for a perfect equilateral triangle is pi/3
    ideal_angle <- pi / 3
    if(is.na(angle2)) {print("#########################");print(i);print(angle2);cat(i,(d23^2 + d12^2 - d31^2) / (2 * d23 * d12),"\n")}
    # Calculate the order for this triangle (how close angles are to ideal)
    to <- c(to,c(angle1,angle2,angle3)*180/pi)
    # Subtract the order value from 1 (closer to 1 means more ordered)
  }
  
  # Normalize by number of triangles
  return(to)
}


### Time-stamping functions
subtract_timestamps <- function(t1, t2) {
  # Function to convert timestamp string to seconds
  # Example usage
  # t1 <- "14.41.37.965"
  # t2 <- "14.41.38.975"
  # subtract_timestamps(t1, t2)
  
  convert_to_seconds <- function(time_str) {
    # Split the string into hours, minutes, seconds, and milliseconds
    time_parts <- unlist(strsplit(time_str, "\\."))
    
    # Extract hours, minutes, seconds and milliseconds
    hours <- as.numeric(time_parts[1])
    minutes <- as.numeric(time_parts[2])
    seconds <- as.numeric(time_parts[3]) + as.numeric(time_parts[4]) / 1000
    
    # Convert the time into total seconds
    total_seconds <- hours * 3600 + minutes * 60 + seconds
    return(total_seconds)
  }
  
  # Convert both timestamps to seconds
  t1_seconds <- convert_to_seconds(t1)
  t2_seconds <- convert_to_seconds(t2)
  
  # Subtract and round to 3 decimal places
  diff_seconds <- round(t2_seconds - t1_seconds, 3)
  
  return(diff_seconds)
}


