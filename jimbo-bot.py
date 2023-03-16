import os

import discord
import discord.ext
from PIL import Image
import pathlib

TEMP_PATH_INPUT = os.environ.get('AVATAR_TEMP_DIRECTORY')
if not TEMP_PATH_INPUT:
    TEMP_PATH: pathlib.Path = pathlib.Path().absolute() / "tmp_avatars"
else:
    TEMP_PATH: pathlib.Path = pathlib.Path(TEMP_PATH_INPUT).absolute()

PROFILE_PATH_BORDER_INPUT = os.environ.get('AVATAR_BORDER', (pathlib.Path().absolute() / "TAC_Profile_Border_256x256.png").as_posix())
PROFILE_PATH_BORDER: pathlib.Path = pathlib.Path(PROFILE_PATH_BORDER_INPUT).absolute()

PROFILE_PATH_MASK_INPUT = os.environ.get('AVATAR_MASK', (pathlib.Path().absolute() / "TAC_Profile_TRANSPARENT_MASK_256x256.png").as_posix())
PROFILE_MASK_BORDER: pathlib.Path = pathlib.Path(PROFILE_PATH_MASK_INPUT).absolute()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
async def get_user_avatar(user: discord.Member) -> pathlib.Path:
    avatar_file: pathlib.Path = TEMP_PATH / f"{user.id}.png"

    await user.avatar.save(avatar_file.absolute().as_posix())

    return avatar_file

def overlay_profile_picture(avatar_base: pathlib.Path, output_file: pathlib.Path):
    avatar_base_image = Image.open(avatar_base)
    profile_border_image = Image.open(PROFILE_PATH_BORDER)
    profile_mask = Image.open(PROFILE_MASK_BORDER)

    avatar_base_image = avatar_base_image.resize((256,256))

    output_image = Image.new('RGBA', avatar_base_image.size)

    output_image.paste(avatar_base_image, (0,0), mask=profile_mask)

    output_image.paste(profile_border_image, (0,0), mask=profile_border_image)

    output_image.save(output_file)

@tree.command(name='tac-frame',
              description='Get a custom Tactical-ified profile picture',
              guild=discord.Object(id=892150703341072494))
async def customize_profile_picture(interaction: discord.interactions.Interaction):
    author = interaction.user
    avatar_file = await get_user_avatar(author)
    output_picture_path: pathlib.Path = TEMP_PATH / f'{author.id}-output.png'
    overlay_profile_picture(avatar_file, output_picture_path)

    dm_channel = await author.create_dm()
    await dm_channel.send('Here is your new Profile Picture!',
                          file=discord.File(output_picture_path.absolute().as_posix()))

    os.remove(avatar_file)
    os.remove(output_picture_path)
    await interaction.response.send_message('Check your DMs, please!', ephemeral=True)
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=892150703341072494))
    print(f'We have logged in as {client.user}')

client.run(os.environ.get('JIMBOT_TOKEN'))