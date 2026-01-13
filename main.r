data = read.csv("bioavailability.csv")
percs = data$percentage

# find MME based on part (a)
thetaMME = 2*mean(percs)/(1-mean(percs))

# view data and model on top
hist(percs, freq=F, xlab = "Absorption Percentage", main = "Bioavailability of Drug in 134 Patients")

xs = seq(0, 1, by=0.01)
ys = (thetaMME^2+thetaMME)*xs^(thetaMME -1)*(1-xs)
lines(xs, ys, col="red")


