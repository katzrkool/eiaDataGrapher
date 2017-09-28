import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

session = requests.session()

#checks for api key, if it exists, it grabs it. Else it asks for it
if os.path.isfile("apiKeyCenter.txt"):
    with open("apiKeyCenter.txt","r") as f:
        apiKey = f.read()
else:
    apiKey = input("No api key detected. Please enter api key. Don't have one? Get one here: https://www.eia.gov/opendata/register.php\n")
    with open("apiKeyCenter.txt", "w") as f:
        f.write(apiKey)

# and if it can't find the text file with urls or its empty, it asks for it
if not os.path.isfile("urls.txt") or os.stat("urls.txt").st_size == 0:
    print("Please put urls for the links you want to download and graphs in a file called 'urls.txt'")
    print("\nExample: http://api.eia.gov/series/?api_key=YOUR_API_KEY_HERE&series_id=INTL.5-2-CAN-MTOE.A")
    sys.exit()

multiple = False

graphNames = []

global bigData
global urlIndex

#using url, it downloads a json with the graph data
def scrapDatData(url, index):
    global graphNames
    data = session.get(url)
    data = json.loads(data.text)
    name = data["series"][0]["name"]
    graphNames.append(name)
    #saves the data in a data folder
    with open("data/{}.json".format(name),"w") as f:
        json.dump(data, f)
    print("Downloaded #{}".format(index))

def grabDatSubPlotSize(numero):
    with open("subPlotSizes.json", "r") as f:
        sizes = json.load(f)
    return int(sizes[str(numero)])

#grabs the list of choices and sends them into the formatter one at a time
def formatPrep(choice):
    global multiple
    global soManyChoose
    soManyChoose = choice
    multiple = True
    global subPlotSize
    subPlotSize = grabDatSubPlotSize(len(choice))
    for i in choice:
        formatDatData(i)
    #sets the space between each minigraph and shows it
    plt.subplots_adjust(hspace = 1)
    plt.show()
    #goes back so the user can pick more graphs after graph window is closed
    choose()


#function to format the json files
def formatDatData(choice):
    global multiple
    global soManyChoose
    #if the user put in multiple graph numbers, it sends the graph choices to a prep function
    if len(choice.split(" ")) > 1:
        choice = choice.split(" ")
        formatPrep(choice)
    else:
        choice = int(choice) - 1
        nameChoice = graphNames[choice]
        #grabs the data from the saved json file
        with open("data/{}.json".format(nameChoice), "r") as f:
            data = json.load(f)

        #setting up the axis, titles, etc
        bigData = data["series"][0]
        data = bigData["data"]
        xAxis = []
        yAxis = []
        title = bigData["name"]
        start = int(bigData["start"])
        end = int(bigData["end"])

        #for each dataset, if the data isn't available (ex: 2015, NA), it kicks it out of the data set to graph
        for i in data:
            if i[1] != "NA" and i[1] != "(s)":
                xAxis.append(i[0])
                yAxis.append(i[1])
        xAxis = np.asarray(xAxis)
        yAxis = np.asarray(yAxis)
        axisLimit = [start,end,0,max(yAxis)]

        # if there are multiple graphs to graph, it is sent to a multiple graphing function, else it's just graphed normally
        if multiple == False:
            graphDatData(xAxis, yAxis, axisLimit,title,bigData["units"])
        else:
            index = soManyChoose.index(str(choice+1)) + 1
            graphAllDatData(xAxis, yAxis, axisLimit, title, bigData["units"], index)

def graphDatData(xAxis, yAxis, axisLimit,title,units):
    #plots axis, sets titles, and shows graph
    plt.plot(xAxis, yAxis)
    plt.axis(axisLimit)
    plt.title(title)
    plt.xlabel("Years")
    plt.ylabel(units)
    plt.show()
    choose()


def graphAllDatData(xAxis, yAxis, axisLimit, title, units, index):
    global subPlotSize
    #subplots allow for multiple graphs on one window
    #using set parameters, it sets up the window with certain sizes (Ex: 2 by 3 graphs). see subPlotSizes.json
    #each graph is plotted in a different subplot
    plt.subplot(int("{}{}".format(subPlotSize,index)))
    plt.plot(xAxis,yAxis)
    plt.axis(axisLimit)
    plt.title(title)
    plt.xlabel("Years")
    plt.ylabel(units)
    #after each subplot has been graphed, the program goes back up to formatPrep to show the graph

#asks which graph(s) to use
def choose():
    global multiple
    multiple = False
    choice = input("Please pick one graph from the list of graphs to graph. Pick multiple to compare.\t")
    formatDatData(choice)

#opens url file and sends all urls to scraper to download
with open("urls.txt","r") as f:
    urlIndex = 0
    for line in f:
        line = line.replace("YOUR_API_KEY_HERE", apiKey)
        urlIndex = urlIndex+1
        scrapDatData(line,urlIndex)

#prints out all the graph names and asks the user which one to use
for i in range(0,len(graphNames)):
    print("{}. {}".format(i+1, graphNames[i]))
choose()

