library(RJSONIO)

parse_illqc_summary <- function(path.to.summary) {
  files <- list.files(path = path.to.summary, pattern = "summary-illqc_")

  for (i in 1:length(files)) {
    x<-fromJSON(files[i])
    d <- x[['data']]
    if (i==1) {
      illqc_sum <- d$illqc
      rname <- substr(files[i], 15, nchar(files[i])-5)
    }
    else {
      illqc_sum <- rbind.data.frame(illqc_sum, d$illqc)
      rname <- c(rname, substr(files[i], 15, nchar(files[i])-5))
    }
  }

  rownames(illqc_sum) <- rname
  colnames(illqc_sum) <- c("input", "both_kept",  "rev_only", "dropped", "fwd_only")
  return (illqc_sum)
}

parse_fastqc_summary <- function(path.to.summary) {
  files <- list.files(path = path.to.summary, pattern = "summary-illqc_")
  
  for (i in 1:length(files)) {
    x<-fromJSON(files[i])
    d <- x[['data']]
    if (i==1) {
      fastqc_sum <- rbind.data.frame(d$fastqc_bef_fwd, d$fastqc_bef_rev, d$fastqc_aft_fwd, d$fastqc_aft_rev)
    }
    else {
      fastqc_sum <- rbind.data.frame(fastqc_sum, d$fastqc_bef_fwd, d$fastqc_bef_rev, d$fastqc_aft_fwd, d$fastqc_aft_rev)
    }
  }
  sample <- substr(files, 15, nchar(files)-5)
  rname <- c(paste(sample, "bef_fwd", sep="-"),
               paste(sample, "bef_rev", sep="-"),
               paste(sample, "aft_fwd", sep="-"),
               paste(sample, "aft_rev", sep="-"))
  
  rownames(fastqc_sum) <- rname
  colnames(fastqc_sum) <- c("Per tile sequence quality", "Per base sequence quality", "Sequence Duplication Levels",
  "Per base sequence content", "Per sequence GC content", "Sequence Length Distribution", "Kmer Content", "Basic Statistics",
  "Adapter Content", "Overrepresented sequences", "Per base N content", "Per sequence quality scores")
  return (fastqc_sum)
}

parse_decontam_summary <- function(path.to.summary) {
  files <- list.files(path = path.to.summary, pattern = "summary-decontam_")
  
  for (i in 1:length(files)) {
    x<-fromJSON(files[i])
    d <- x[['data']]
    if (i==1) {
      decontam_sum <- d
      rname <- substr(files[i], 18, nchar(files[i])-5)
    }
    else {
      decontam_sum <- rbind.data.frame(decontam_sum, d)
      rname <- c(rname, substr(files[i], 18, nchar(files[i])-5))
    }
  }
  
  rownames(decontam_sum) <- rname
  colnames(decontam_sum) <- c("Non-Human_Reads", "Human_Reads")
  Percent_Human = (decontam_sum$Human_Reads * 100)/(decontam_sum$Human_Reads + decontam_sum$`Non-Human_Reads`)
  decontam_sum = cbind(decontam_sum, Percent_Human)
  return (decontam_sum)
}

parse_phix_summary <- function(path.to.summary) {
  files <- list.files(path = path.to.summary, pattern = "summary-phix_")
  
  for (i in 1:length(files)) {
    x<-fromJSON(files[i])
    d <- x[['data']]
    if (i==1) {
      phix_sum <- d
      rname <- substr(files[i], 14, nchar(files[i])-5)
    }
    else {
      phix_sum <- rbind.data.frame(phix_sum, d)
      rname <- c(rname, substr(files[i], 14, nchar(files[i])-5))
    }
  }
  
  rownames(phix_sum) <- rname
  colnames(phix_sum) <- c("Non-Human_Reads", "Human_Reads")
  Percent_Human = (phix_sum$Human_Reads * 100)/(phix_sum$Human_Reads + phix_sum$`Non-Human_Reads`)
  phix_sum = cbind(phix_sum, Percent_Human)
  return (phix_sum)
}

path.to.summary <- "/home/ashwini/ash/baylor_samples/lane3/analysis/summary"
x <- parse_illqc_summary(path.to.summary)
xd <- parse_decontam_summary(path.to.summary)
xf <- parse_fastqc_summary(path.to.summary)

stargazer(x, summary = FALSE, title = "Summary table after qualtiy control.")
stargazer(xd, summary = FALSE, title = "Summary table after Human filtering reads.")
