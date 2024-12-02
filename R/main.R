source("auxiliary_functions.R")

# Provide a vector with the filenames you want to analyze
# e.g.: 
# filenames <- c("save-2023.11.07-14.41.37.965-points.csv",
#                      "save-2023.11.07-14.42.39.766-points.csv",
#                      "save-2023.11.07-14.44.00.106-points.csv",
#                      "save-2023.11.07-14.45.43.106-points.csv",
#                      "save-2023.11.07-14.48.18.636-points.csv",
#                      "save-2023.11.07-14.51.18.176-points.csv")

all_dfs <- list()
for(i in 1:7) {
  # all_dfs[[i]] <- read_csv(sprintf("%s%s%s",prefix,filenames[i],suffix),
  all_dfs[[i]] <- read_csv(sprintf("%s%s",prefix,filenames[i]),
                           col_types = cols(filename = col_skip()))
}

all_outputs <- list()
for(i in 1:7) {
  all_outputs[[i]] <- datavoronoi(all_dfs[[i]])
}
par(mfrow=c(1,1))
i <- 1
plotlemaitre(all_outputs[[i]],mypch = "1",mycex=1.3)
print(all_outputs[[i]]$lem[1])
for(i in 2:7) {
  plotlemaitre(all_outputs[[i]], add = TRUE, defaultcol = i,mypch=as.character(i),mycex=1.3)
  print(all_outputs[[i]]$lem[1])
}

x11("",16,9)
par(mfrow=c(2,7))
for(i in 1:7) {
  plot(all_outputs[[i]]$triangles,main=sprintf("%s",filenames[i]))
}

# par(mfrow=c(3,2))
for(i in 1:7) {
  voronoi <- with(all_dfs[[i]],deldir(x, y))
  voronoi_areas <- voronoi$summary$dir.area
  ind <- all_outputs[[i]]$triangles$PB==0
  h <- hist(voronoi_areas[ind],probability = TRUE,border='white',col='#FF7F0Eaa')
  abline(v=median(voronoi_areas),lwd=3)
  print(median(voronoi_areas))
  print(h$mid[which.max(h$density)])
  print(sd(voronoi_areas[ind]))
  print("-----")
}

# After processing the files, say, for 12nM, you can save the analysis in binary
# format for posterior manipulations
# saveRDS(all_dfs,"all_dfs_12nM.rda")
# saveRDS(all_outputs,"all_outputs_12nM.rda")
# Repeat for all files/folders

####### Angle analysis
# Read the rda files created iteratively above
df_files <-   dir(".",pattern="all_dfs")[c(1,3,5,7,9)]
df_files <-  df_files[c(3,4,5,1,2)]

x11("",16,8)
all_p_60 <- list()
df_list <- list()
names2 <- c()
for(j in 1:5) {
  cat("---->",df_files[j],"\n")
  df_list[[j]] <- readRDS(df_files[j])
  names2 <- c(names2,strsplit(df_files[j],".rda")[[1]])
  par(mfrow=c(2,3))
  par(mar=c(5,5,3,3))
  angles <- list() 
  aux <- c()
  for(i in 1:length(df_list[[j]])) {
    angles[[i]] <-  angle_distr(df_list[[j]][[i]])
    angs <- round(as.vector(angles[[i]])/10)*10 
    tb <- table(angs)/length(angs)
    tb <- table(angs)
    p_60 <- tb |> as.data.frame() |> filter(angs==60)
    aux <- c(aux,p_60[2])
    hist(angles[[i]],25,main=sprintf("#of angles around 60º:%.0f    #of triangles: %.0f",p_60[2],length(angs)/3),
         border='white',col='skyblue',xlab=expression(theta),cex.axis=1.5,cex.lab=1.5)
    abline(v=60,lwd=3)
  }
  all_p_60[[j]] <- aux
}

x11("",6,6)
par(mar=c(5,5,3,3))
par(mfrow=c(1,1))

names(all_p_60) <- names2
legends <- c("4","6","8","10","12")
legendsnM <- c("4nM","6nM","8nM","10nM","12nM")
plot(c(0,1250),c(0,90),type='n',xlab='time (s)',ylab="#of angles around 60º",cex.axis=1.5,cex.lab=1.5)
for(i in 1:5) {
  points(times_list[[i]],all_p_60[[i]],col=i,lwd=1.5,pch=20+i,type='b',cex=1.5,bg=i)
}

legend('bottomright',legend=legendsnM,col=1:5,lwd=2,cex=1.5,pch=21:25,pt.bg=1:5)