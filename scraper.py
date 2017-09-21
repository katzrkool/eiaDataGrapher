import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

session = requests.session()

if os.path.isfile("apiKeyCenter.txt"):
    with open("apiKeyCenter.txt","r") as f:
        apiKey = f.read()
else:
    apiKey = input("No api key detected. Please enter api key. Don't have one? Get one here: https://www.eia.gov/opendata/register.php\n")
    with open("apiKeyCenter.txt", "w") as f:
        f.write(apiKey)

if not os.path.isfile("urls.txt") or os.stat("urls.txt").st_size == 0:
    print("Please put urls for the links you want to download and graphs in a file called 'urls.txt'")
    print("\nExample: http://api.eia.gov/series/?api_key=YOUR_API_KEY_HERE&series_id=INTL.5-2-CAN-MTOE.A")
    sys.exit()

multiple = False

graphNames = []

global bigData
global urlIndex

def scrapDatData(url, index):
    global graphNames
    data = session.get(url)
    data = json.loads(data.text)
    name = data["series"][0]["name"]
    graphNames.append(name)
    with open("data/{}.json".format(name),"w") as f:
        json.dump(data, f)
    print("Downloaded #{}".format(index))

def grabDatSubPlotSize(numero):
    with open("subPlotSizes.json", "r") as f:
        sizes = json.load(f)
    return int(sizes[str(numero)])

def formatPrep(choice):
    global multiple
    global soManyChoose
    soManyChoose = choice
    multiple = True
    global subPlotSize
    subPlotSize = grabDatSubPlotSize(len(choice))
    for i in choice:
        formatDatData(i)
    plt.subplots_adjust(hspace = 1)
    plt.show()
    choose()

def formatDatData(choice):
    global multiple
    global soManyChoose
    if len(choice.split(" ")) > 1:
        choice = choice.split(" ")
        formatPrep(choice)
    else:
        choice = int(choice) - 1
        nameChoice = graphNames[choice]
        with open("data/{}.json".format(nameChoice), "r") as f:
            data = json.load(f)
        bigData = data["series"][0]
        data = bigData["data"]
        xAxis = []
        yAxis = []
        title = bigData["name"]
        start = int(bigData["start"])
        end = int(bigData["end"])
        for i in data:
            if i[1] != "NA" and i[1] != "(s)":
                xAxis.append(i[0])
                yAxis.append(i[1])
        xAxis = np.asarray(xAxis)
        yAxis = np.asarray(yAxis)
        axisLimit = [start,end,0,max(yAxis)]
        if multiple == False:
            graphDatData(xAxis, yAxis, axisLimit,title,bigData["units"])
        else:
            index = soManyChoose.index(str(choice+1)) + 1
            graphAllDatData(xAxis, yAxis, axisLimit, title, bigData["units"], index)

def graphDatData(xAxis, yAxis, axisLimit,title,units):
    plt.plot(xAxis, yAxis)
    plt.axis(axisLimit)
    plt.title(title)
    plt.xlabel("Years")
    plt.ylabel(units)
    plt.show()
    choose()


def graphAllDatData(xAxis, yAxis, axisLimit, title, units, index):
    global subPlotSize
    plt.subplot(int("{}{}".format(subPlotSize,index)))
    plt.plot(xAxis,yAxis)
    plt.axis(axisLimit)
    plt.title(title)
    plt.xlabel("Years")
    plt.ylabel(units)


def choose():
    global multiple
    multiple = False
    choice = input("Please pick one graph from the list of graphs to graph. Pick multiple to compare.\t")
    formatDatData(choice)

with open("urls.txt","r") as f:
    urlIndex = 0
    for line in f:
        line = line.replace("YOUR_API_KEY_HERE", apiKey)
        urlIndex = urlIndex+1
        scrapDatData(line,urlIndex)

for i in range(0,len(graphNames)):
    print("{}. {}".format(i+1, graphNames[i]))
choose()

