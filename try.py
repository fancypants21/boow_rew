import goslate

text = "I liked this shit"

gs = goslate.Goslate()
translatedText = gs.translate(text,'tr')

print(translatedText)
