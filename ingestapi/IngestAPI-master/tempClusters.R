#In this file we loop through all of our EMRs, create subgraphs and linkbacks
#corresponding to each subgraph. We store them in our local folder
rm(list = ls()) #clear workspace
cat("\014")  #clear console

library(tm)
library(stringr)
library(wordcloud)
library(igraph)
library(SnowballC)
library(networkD3)

substrLeft <- function(x, n){
  return(substr(x, 1, nchar(x)))
}

GetTitle<-function(filename) {
  if(filename == "AppendicitisCommentsPT9.txt") {
    return("Communities in Appendicitis network")
  }else if (filename == "SyncopeCommentsPT14.txt") {
    return("Communities in Syncope network")
  } else if (filename == "ChestPainPT50Comments.txt") {
    return("Communities in Chest Pain network")
  } else if (filename == "ChronicRenalDiseaseHIVPT48Comments.txt") {
    return("Communities in Chronic Renal Disease Network") 
  } else if (filename == "HypercalcemiaParathyroidAdenomaPT45.txt") {
    return("Communities in Hypercalcemia Network") 
  } else if (filename == "PainPT18Comments.txt") {
    return("Communities in Pain network")
  } else if (filename == "anemiaCommentsPT26.txt") {
    return("Communities in Anemia network") 
  } else if (filename == "colonCancerCommentsPT10.txt") {
    return("Communities in Colon Cancer network")
  } else if (filename == "diabetesCommentsPT30.txt") {
    return("Communities in Diabetes network")
  } else if (filename == "lungcancerCommentsPT38.txt") {
    return("Communities in Lung Cancer network")
  } else {
    return("Communities")
  }
}

#clean a single EMR
CleanText<-function(text)
{
  text<-str_replace_all(text, "  "," ") #redundant spaces
  text<-str_replace_all(text, "XXX[a-z,A-Z,0-9]"," ") #redundant x's in headers
  text<-str_replace_all(text,"[0-9]", "") #numbers
  text<-str_replace_all(text,"http://t.co/[a-z,A-Z,0-9]{8}", "") #URLs
  text<-str_replace_all(text,"RT @[a-z,A-Z]*: ", "") #retweet headers
  text<-str_replace_all(text,"#[a-z,A-Z]*","") #hashtags
  text<-str_replace_all(text, "@[a-z,A-Z]*","") #screennames
  text<-str_replace_all(text, "[^[:alnum:]]", " ") #remove all non-alphanumeric characters
  return(text)
}

#cleans individual documents
CleanDocument<-function(sentence) {
  sentence = gsub('[[:punct:]]', '', sentence)
  sentence = gsub('[[:cntrl:]]', '', sentence)
  sentence = gsub('\\d+', '', sentence)
  # and convert to lower case:
  sentence = tolower(sentence)
  
  # split into words. str_split is in the stringr package
  word.list = str_split(sentence, '\\s+')
  # word.list = str_split(sentence, ".")
  words = unlist(word.list)
  return(words)
}

#here we generate the subgraphs and store them as PNGs and print corresponding raw text document
ComputeClusters<-function(spp, listGraphs, RiskScores.txt, graph_title, dic)
{
  #if number of vertices is less than 50 then recurse otherwise just plot
  num_nodes<-vcount(spp)
  #print(paste("Number of nodes in our graph is ", num_nodes, sep = ""))
  #print(spp$name)
  
  #plots the current graph with its clusters and outputs the raw text
  
  file_out_graph = paste("/Users/gangopad/Company/REST/Data/Temp/PNGs/", spp$name, ".txt.png", sep="")
  file_out_text = paste("/Users/gangopad/Company/REST/Data/Temp/Text/", spp$name, ".txt", sep="")
  file_out_nodes = paste("/Users/gangopad/Company/REST/Data/Temp/Nodes/", spp$name, ".txt", sep="")
  file_out_html = paste("/Users/gangopad/Company/REST/Data/Temp/HTML/", spp$name, ".html", sep="")
  
  vertex_names<- V(spp)$name
  fg<-fastgreedy.community(spp)
  V(spp)$com<-fg$membership
  #print(V(spp))
  
  if (num_nodes < 50 || length(fg) == 1) {
    #find document closest corresponding to current graph
    current_doc = ""
    max_score = -1
    max_doc = current_doc #text associated with maximum intersection between graph and text
    for (i in 1:length(RiskScores.txt)){
      if(RiskScores.txt[[i]] == "") {
        words<-CleanDocument(current_doc)
        #print(words)
        score = length(intersect(vertex_names, words))
        #print(paste("The score is ", score, ""))
        
        if(score > max_score) {
          max_score= score
          max_index = i
          max_doc = current_doc
        }
        
        current_doc = ""
        
      } else {
        current_doc = paste(current_doc, RiskScores.txt[[i]], sep = "\n")
      }
      
    }
    
      fileConn<-file(file_out_text)
      writeLines(max_doc, fileConn)
      close(fileConn)
    
      #print(V(spp)$name)
      fileConn<-file(file_out_nodes)
      writeLines(V(spp)$name, fileConn)
      close(fileConn)
    
      #Output only leaf nodes as png (compute size of communities)
      if (num_nodes < 10) {
        png(filename=file_out_graph, height=800, width=600)
        plot(fg, spp,vertex.shape="none", vertex.label.cex=3, vertex.label.font = 2)
        title(graph_title, cex.main = 3)
        dev.off()
        
        spp <- get.data.frame(spp, what = "edges")
        simpleNetwork(spp, fontSize = 12)
        
        
      } else if (num_nodes < 20) {
        png(filename=file_out_graph, height=1400, width=1100)
        plot(fg, spp,vertex.shape="none", vertex.label.cex=3, vertex.label.font = 2)
        title(graph_title, cex.main = 3)
        dev.off()
        
        spp <- get.data.frame(spp, what = "edges")
        simpleNetwork(spp, fontSize = 12)
        
      } else if (num_nodes < 30) {
        png(filename=file_out_graph, height=1600, width=1200)
        plot(fg, spp,vertex.shape="none", vertex.label.cex=3, vertex.label.font = 2)
        title(graph_title, cex.main = 3)
        dev.off()
        
        spp <- get.data.frame(spp, what = "edges")
        simpleNetwork(spp, fontSize = 12)
        
      } else {
        png(filename=file_out_graph, height=2000, width=1500)
        plot(fg, spp,vertex.shape="none", vertex.label.cex=3, vertex.label.font = 2)
        title(graph_title, cex.main = 3)
        dev.off()
        
        spp <- get.data.frame(spp, what = "edges")
        simpleNetwork(spp, fontSize = 12)
        
      }
  } else {
    
    #MAKE A NEW GRAPH WITH NODES BEING CLUSTERS AND NODE NAME BEING TOP 5 DEGREE NODES
    
    
    #We add to queue for each community (at the end of the queue):
    #print("new cluster")
    for(i in 1:length(fg))  {
        spp.1<-delete.vertices(spp, !(V(spp)$com %in% i))
        spp.1$name<-paste(spp$name, ".", i, sep="")
        #print(max(degree(spp.1))$name)
        #V(spp.1)$deg<-degree(spp.1)
        #max.spp.1<-max(V(spp.1)$deg)
        #print(paste(V(spp.1)[deg==max.spp.1]$name, ", ", max.spp.1, sep=""))
        listGraphs[[length(listGraphs)+1]] <- spp.1
    }
  }
  
  return(listGraphs)
}



#AT THIS POINT, LOAD DICTIONARY (dictionary.txt) AND SUBSTITUTE CUI WIH PT
dictTable<-read.table("/Users/gangopad/Company/RiskScores/dictionary.txt", sep = "\t", quote = "", header= TRUE)
dic<-as.vector(dictTable[['PT']])
names(dic)<-as.vector(dictTable[['CUI']])
names(dic)<-tolower(names(dic))

files <- list.files(path="/Users/gangopad/Company/REST/Data/Temp/Data", pattern="*.xml", full.names=T, recursive=FALSE)
lapply(files, function(x) {
  print(paste("Reading file ", x, sep = ""))
  
  #data represents the original data in cleaned form and CleanedData has the CUIs substituted in 
  orig_docs<-readLines(paste("/Users/gangopad/Company/REST/Data/Temp/Data/", basename(x), sep = ""))
  docs <-readLines(x)
  RiskScores.txt<-CleanText(docs)
  
  RiskScores.corpus<-Corpus(VectorSource(RiskScores.txt))
  RiskScores.corpus<-tm_map(RiskScores.corpus,removeWords,stopwords('english'))
  #print(RiskScores.corpus)
  
  RiskScores.tdm<-TermDocumentMatrix(RiskScores.corpus)
  
  RiskScores.matrix<-as.matrix(RiskScores.tdm)
  bg<-graph.incidence(RiskScores.matrix)
  spp<-bipartite.projection(bg, multiplicity = TRUE)[[1]]
  spp$name<-basename(x)
  title<-GetTitle(spp$name)
  
  #newnames<-V(spp)$name
  #print(class(V(spp)$name))
  #substitute cui with pt
  #for (node in V(spp)$name) {
  #  if (node %in% names(dic)) {
   #       index<-dic[[node]]
          #print(index)
    #      if (index == "") {
            #print(node)
     #     } else {
      #    newnames = gsub(node, index, newnames)
       #   }
          #print("Substituting CUI")
  #}
#}
  #spp <- set.vertex.attribute(spp, "name", value=newnames)
  #print(V(spp)$name)
  
  #Keep running until queue is empty. First call will be just a queue with the whole graph
  listGraphs <- list(spp)
  #print("Computing subclusters here")
  while(length(listGraphs) > 0){
    spp <- listGraphs[[1]]
    listGraphs<-ComputeClusters(spp, listGraphs, orig_docs, title, dic)
    listGraphs[[1]] <- NULL
    #print(length(listGraphs))
  }
})
