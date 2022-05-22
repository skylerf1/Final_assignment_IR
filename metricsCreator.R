library(data.table)
library(rjson)
library(ggplot2)

data <- fread('results.csv')
boe <- names(data)

plotter <- function(columns, file_path) {
	aggregated_data <- data.table(
		metrics = factor(columns, levels = columns),
		meanie = unlist(data[, lapply(.SD, mean), .SDcols = columns]),
		error = unlist(data[, lapply(.SD, sd), .SDcols = columns])
	)
	aggregated_data[, lapply(.SD, class)]
	
	p <- ggplot(aggregated_data, aes(x=factor(metrics), y=meanie, fill='#00cc00'))
	p <- p + geom_bar(stat="identity", color="black", position=position_dodge())
	p <- p + geom_errorbar(aes(ymin=meanie-error, ymax=meanie+error),
						   width=.2, position=position_dodge(.9))
	
	
	# Finished bar plot
	p <- p + labs(x="Metric", y = "Value (mean)")
	p <- p + theme_classic()
	p <- p + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1), legend.position = 'none')
	
	ggsave(file_path, dpi = 1000L)
	return(p)
}

plotter(boe[60L:68L], 'ndcg.png')
plotter(boe[32L:40L], 'recall.png')

