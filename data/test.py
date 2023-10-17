import json

# Read the JSON file
with open('hamzah.json', 'r') as file:
    data = json.load(file)

# Extract words and their geometry
words = []
for page in data['pages']:
    for block in page['blocks']:
        for line in block['lines']:
            for word in line['words']:
                value = word['value']
                geometry = word['geometry'][0][1]  # Extract y coordinate
                words.append((value, geometry))

# Sort words based on their y geometry
words.sort(key=lambda x: x[1])

# Group words with the same y geometry and print them on the same line
current_y = words[0][1]
line_words = []
for word, y in words:
    if y == current_y:
        line_words.append(word)
    else:
        print(' '.join(line_words))
        line_words = [word]
        current_y = y

# Print the last line
if line_words:
    print(' '.join(line_words))