import json
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import re
import os
import shutil

def delete_directory_contents(directory):
    """Delete the contents of a directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def add_black_section(image_path, output_path, section_height):
    # Open the image and resize if necessary
    img = Image.open(image_path)
    if img.size[1] < section_height:
        img = img.resize((img.size[0], section_height))

    # Add the black section at the top of the image
    black_section = ImageOps.expand((img.size[0], section_height), color='black')
    img = ImageOps.crop(img, (0, section_height, 0, 0))
    img = Image.alpha_composite(black_section, img)

    # Save the image to the output path
    img.save(output_path)

def generate_completion(api_key, prompt_text=""):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
      "model": "text-davinci-003",
      "prompt": prompt_text,
      "max_tokens": 3800,
      "temperature": 0
    }

    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)

    return response.json()

def generate_image_from_text(text, filename):
    print("Generating image for " + text)
    api_key = os.environ.get('DEEPAI_API_KEY')
    headers = {'api-key': api_key}
    data = {'text': text, "grid_size" : 1}
    response = requests.post('https://api.deepai.org/api/text2img', headers=headers, data=data)
    response_dict = json.loads(response.text)
    try:
        output_url = response_dict['output_url']
    except KeyError:
        print(response_dict)
    img_response = requests.get(output_url)
    with open(f'output/{filename}.jpg', 'wb') as f:
        f.write(img_response.content)

def convert_images(input_dir, output_dir, output_format="PNG"):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Loop over all images in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            # Open the JPEG image and convert it to the output format
            with Image.open(os.path.join(input_dir, filename)) as image:
                image = image.convert("RGBA") # Convert to RGBA mode
                output_filename = os.path.splitext(filename)[0] + "." + output_format.lower() # Change the extension to the output format
                output_filepath = os.path.join(output_dir, output_filename)
                image.save(output_filepath, format=output_format) # Save as output format

def generate_gif(frames, output_path, duration=5000, font_size=15):
    # Open the images and resize them to the same size

    # Create a font object for the text
    font = ImageFont.truetype("font/LiberationSansNarrow-Bold.ttf", font_size)

    # Add text and 40% opacity black layer to each image
    images_with_text = []
    for _, frame in enumerate(frames):
        image = Image.open(frame["image"])

        # Add a 40% opacity black layer
        black_layer = Image.new("RGBA", image.size, color=(0, 0, 0, int(255 * 0.5)))
        image = Image.alpha_composite(image, black_layer)
        y = image.height - 100
        draw = ImageDraw.Draw(image)

        sentences = split_long_sentence(frame["text"])
        for sentence in sentences:
            # Draw the text
            draw.text((5, y), sentence, fill="yellow", font=font, align="left")
            y += font_size + 2        
        images_with_text.append(image)

    # Save the GIF with the text and 40% opacity black layer
    images_with_text[0].save(output_path, save_all=True, append_images=images_with_text[1:], duration=duration, loop=0)      

def split_long_sentence(text, max_sentence_length=75):
    sentences = re.split('\.', text)
    sentences = [sentence.strip() for sentence in sentences]

    new_sentences = []
    for sentence in sentences:
        if len(sentence) > max_sentence_length:
            new_sentence = sentence
            while len(new_sentence) > max_sentence_length:
                split_point = max_sentence_length
                while split_point > 0 and new_sentence[split_point] != " ":
                    split_point -= 1
                if split_point == 0:
                    # If no space found, split at max_sentence_lengthth character
                    split_point = max_sentence_length
                new_sentences.append(new_sentence[:split_point].strip())
                new_sentence = new_sentence[split_point:].strip()
            new_sentences.append(new_sentence)
        else:
            new_sentences.append(sentence)
    return new_sentences

parser = argparse.ArgumentParser(description='Generate images from adventure story choices.')
parser.add_argument('--prompt', type=str, help='the prompt text for the adventure story')
parser.add_argument('--disable-delete', action='store_true', help='disable the delete_directory_contents function')
parser.add_argument('--disable-image', action='store_true', help='disable the generate_image_from_text function')
parser.add_argument('--disable-both', action='store_true', help='disable both delete_directory_contents and generate_image_from_text functions')
args = parser.parse_args()

if __name__ == "__main__":
    isExist = os.path.exists("./output")
    if not isExist:
        os.makedirs("./output")    
    # Read the story from the JSON file
    if not args.disable_both and not args.disable_delete:
        delete_directory_contents("output")

    prompt = args.prompt + ". Mention the prompt details in each sentence. Output each sentence in a JSON list."
    raw_completion = generate_completion(os.environ['CHATGPT_API_KEY'], prompt)
    raw_json = raw_completion["choices"][0]['text']
    story = json.loads(raw_json)
    
    for i, paragraph in enumerate(story):
        if not args.disable_both and not args.disable_image:
            generate_image_from_text(paragraph, i)

    convert_images("output", "output")

    paths = [{"image": f"output/{i}.png", "text": paragraph} for i, paragraph in enumerate(story)]
    generate_gif(paths, "output.gif")


