from PIL import Image
import sys, random, urllib.request, io, time

start_time = time.time()
myUserId = "2020slamsal"

def distance(x, y):
    return ((x[0]-y[0])**2 + (x[1]-y[1])**2 + (x[2]-y[2])**2)**0.5

def getLength(cluster):
    totalLength = 0
    for color in cluster:
        totalLength += distinctPixels[color]
    return totalLength

def calculateMeans(clusters):
    global distinctPixels
    newMeans = []
    for s in clusters:
        new_mean = [0, 0, 0]
        length = 0
        for color in s:
            length += distinctPixels[color]
            new_mean[0] += color[0] * distinctPixels[color]
            new_mean[1] += color[1] * distinctPixels[color]
            new_mean[2] += color[2] * distinctPixels[color]
        new_mean[0] /= length
        new_mean[1] /= length
        new_mean[2] /= length
        newMeans.append(new_mean)
    return newMeans

def neighbors(coord):
    nbrs = set()

    if coord[0] > 0: nbrs.add((coord[0] - 1, coord[1]))
    if coord[0] < size[0] - 1: nbrs.add((coord[0] + 1, coord[1]))
    if coord[1] > 0: nbrs.add((coord[0], coord[1] - 1))
    if coord[1] < size[1] - 1: nbrs.add((coord[0], coord[1] + 1))
    if coord[0] < size[0] - 1 and coord[1] < size[1] - 1: nbrs.add((coord[0] + 1, coord[1] + 1))
    if coord[0] > 0 and coord[1] > 0: nbrs.add((coord[0] - 1, coord[1] - 1))
    if coord[0] > 0 and coord[1] < size[1] - 1: nbrs.add((coord[0] - 1, coord[1] + 1))
    if coord[0] < size[0] - 1 and coord[1] > 0: nbrs.add((coord[0] + 1, coord[1] - 1))

    return nbrs

def floodFill(pixels):
    regionCounts = [0 for x in range(k)]
    coordinates = {(x, y) for x in range(size[0]) for y in range(size[1])}

    while coordinates:
        randCoord = random.sample(coordinates, 1)[0]
        regionCounts[roundedMeans.index(pixels[randCoord[0], randCoord[1]])] += 1
        q = [randCoord]

        while q:
            node = q.pop(0)
            coordinates.remove(node)

            for nbr in neighbors(node):
                if pixels[nbr[0], nbr[1]] == pixels[node[0], node[1]] and nbr in coordinates and nbr not in q:
                    q.append(nbr)


    return regionCounts

k = int(sys.argv[1])
filename = sys.argv[2]

img = ''

if filename[:4] == 'http':
    f = io.BytesIO(urllib.request.urlopen(filename).read())
    img = Image.open(f)
else:
    img = Image.open(filename)

size = img.size
pix = img.load()

means = []
while len(means) != k:
    randX = random.uniform(0, size[0])
    randY = random.uniform(0, size[1])
    if pix[randX, randY] not in means:
        means.append(pix[randX, randY])

clusters = [set() for x in range(k)]
oldClusters = None
distinctPixels = {}
mostCommon = (None, 0)
meanList = {}


for x in range(size[0]):
    for y in range(size[1]):
        if not any([pix[x, y] in s for s in clusters]):
            distances = [distance(pix[x, y], z) for z in means]
            clusters[distances.index(min(distances))].add(pix[x, y])

        if pix[x, y] not in distinctPixels:
            distinctPixels[pix[x, y]] = 1
        else:
            distinctPixels[pix[x, y]] += 1

for x in distinctPixels:
    if distinctPixels[x] > mostCommon[1]:
        mostCommon = (x, distinctPixels[x])

print("Size: {} x {}".format(size[0], size[1]))
print("Pixels: {}".format(size[0] * size[1]))
print("Distinct pixel count: {}".format(len(distinctPixels)))
print("Most common pixel: {} => {}".format(mostCommon[0], mostCommon[1]))
print([len(x) for x in clusters])

i = 0
while clusters != oldClusters:
    seen = set()
    oldClusters = clusters
    means = calculateMeans(clusters)
    clusters = [set() for x in range(k)]
    for x in range(size[0]):
        for y in range(size[1]):
            if pix[x, y] not in seen:
                distances = [distance(pix[x, y], z) for z in means]
                clusters[distances.index(min(distances))].add(pix[x, y])
                meanList[pix[x, y]] = distances.index(min(distances))
                seen.add(pix[x, y])
    print("Iter {}: {}".format(i, [getLength(x) - getLength(oldClusters[q]) for q, x in enumerate(clusters)]))
    i += 1

for x in range(size[0]):
    for y in range(size[1]):
        pix[x, y] = tuple(round(i) for i in means[meanList[pix[x, y]]])

print("Final means:")
for i, mean in enumerate(means, 1):
    print("{}: {} => {}".format(i, mean, getLength(clusters[i - 1])))

img.save("kmeans/{}.png".format(myUserId), "PNG")

roundedMeans = [(round(i[0]), round(i[1]), round(i[2])) for i in means]

regionCounts = floodFill(pix)
print("Region counts: {}".format(regionCounts))

#img.show()
#print(f"elapsed time: {time.time() - start_time}")
