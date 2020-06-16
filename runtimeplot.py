import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv
import argparse
import sys

def labelpercentage(xdata,ydata,percentage):
    indexat30s = next(x for x, val in enumerate(xdata) if val > 0.5)
    outputat30s = ydata[indexat30s]
    target = outputat30s * percentage / 100
    targetindex = next(i for i, val in enumerate(ydata[indexat30s:]) if val < target) + indexat30s
    xpos = xdata[targetindex]
    ypos = ydata[targetindex]
    if xpos < 60:
        timestring = "{:.0f} min".format(xpos)
    else:
        timestring = "{:.1f} h".format(xpos/60)
    plt.annotate("{} to {}%".format(timestring,percentage),(xpos,ypos))

parser = argparse.ArgumentParser(description='Plot runtime graphs from csv files where the the first column is time and the second is output')
parser.add_argument('-t','--title', help='title for the plot',default='Runtime')
parser.add_argument('filenames', help='list of csv files to be plotted', nargs='+')
parser.add_argument('-l','--labels', help='list of labels for the plotted files', nargs='+')
parser.add_argument('-d','--duration',help='maximum value on the x axis',type=float)

args = parser.parse_args()

if args.filenames:
    filenames = args.filenames
else:
    sys.exit('No files specified')

if args.labels and len(args.labels) == len(filenames):
    labels = args.labels
else:
    print('No labels provided, or the number of labels provided does not match')
    labels = range(len(filenames))

title = args.title
fig = plt.figure(figsize=(15,7.5))

for i,filename in enumerate(filenames):
    time = []
    relativeoutput = []
    with open(filename,'r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        next(data)
        for row in data:
            time.append(float(row[0]))
            relativeoutput.append(float(row[1]))
    tstart = time[1]
    time = [(x - tstart) / 60 for x in time]
    if i == 0:
        indexat30s = next(x for x, val in enumerate(time) if val > 0.5)
        firstfileoutputat30s = relativeoutput[indexat30s]
    relativeoutput = [(y / firstfileoutputat30s)*100 for y in relativeoutput]
    labelpercentage(time,relativeoutput,50)
    labelpercentage(time,relativeoutput,10)
    plt.plot(time,relativeoutput,label=labels[i])

plt.xlim(left=0)
if args.duration:
    plt.xlim(right=args.duration)
plt.xlabel('Time [minutes]')
plt.ylabel('Relative Output')
plt.title(title)
plt.tight_layout()
plt.grid(True)
ax = plt.subplot(1,1,1)
ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(15))
ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
plt.text(0.02, 0.02, 'bmengineer.com', transform=ax.transAxes, alpha = 0.5)
plt.legend()
plt.show()
