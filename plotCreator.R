library(data.table)
library(ggplot2)
library(plotly)

dt <- fread('freqs.txt', col.names = c('count', 'docID', 'relevance'))

plotDT <- dt[, .N, by = c('count', 'relevance')]
setkeyv(plotDT, c('count', 'relevance', 'N'))

emptyDT <- data.table(count = rep(seq(75L), each = 3), relevance = rep(c(0L, 1L, 2L), 75L), N = 0L)
setkeyv(emptyDT, c('count', 'relevance', 'N'))

mergedDT <- unique(merge(emptyDT, plotDT, all = TRUE), by = c('count', 'relevance'), fromLast = TRUE)

p <- ggplot(mergedDT, aes(factor(count), factor(N), fill = factor(relevance)))
p <- p + geom_bar(position = 'dodge', stat = 'identity')
p <- p + xlab('Number Of Occurences')
p <- p + ylab('Frequency')
p <- p + scale_fill_manual(name = "Relevance", labels = c("Irrelevant", "Omitted", "Relevant"), values = c("#C70039", "#009EFF", "#2EFF00"))
p <- p + scale_x_discrete(breaks = seq(0, 75L, 5L))
p <- p + theme_bw()
p <- p + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

ggsave('relevance_histogram.png', width = 7.17, height = 2.8, dpi = 1000L)

p




# Create Data
data <- data.table(Relevance = factor(c("Irrelevant", "Relevant", "Omitted")), values = c(24243, 5570, 6019))

# Basic piechart
fig <- plot_ly(data, labels = ~Relevance, values = ~values, type = 'pie', sort = FALSE, marker = list(colors = c("#C70039", "#2EFF00", "#009EFF")))
fig <- fig %>% layout(xaxis = list(showgrid = FALSE, zeroline = FALSE, showticklabels = FALSE),
					  yaxis = list(showgrid = FALSE, zeroline = FALSE, showticklabels = FALSE))

fig

