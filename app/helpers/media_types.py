# Considered having a full tree structure for media types (e.g. "Visual Media" -> "Movie" -> "Action Movie")
# but for the purposes of this project it is unnecessary

# Note that this app was intended to track media TITLES, not all the media you consume 
# (e.g. if you listen to 2 hours of music, you don't need to track the individual songs)
# Feel free to add more media types as needed

def get_main_media_type(type):
    media_types = {
        "Visual Media": ["Movie", "TV Show", "Documentary", "Anime", "Short Film", "Theater Play"],
        "Audio Media": ["Podcast", "Music", "Audiobook"],
        "Text Media": ["Book", "Article", "Blog", "News", "Comic", "Manga", "Webtoon", "Graphic Novel", "Light Novel", "Novel", "Short Story", "Web Novel"],
        "Interactive Media": ["First Person Shooter", "Role Playing Game", "Simulation", "Puzzle", "Platformer", "Strategy", "Adventure"],
    }

# Honestly this file doesn't do much delete if needed