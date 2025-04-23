from PIL import Image
img = Image.open('icon_bot.png')
width, height = img.size
new_height = 24
new_width = int((new_height / height) * width)
img = img.resize((new_width, new_height))
img.save('icon_bot16.png')

img = Image.open('icon.png')
width, height = img.size
new_height = 24
new_width = int((new_height / height) * width)
img = img.resize((new_width, new_height))
img.save('icon16.png')