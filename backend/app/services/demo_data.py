"""Demo data for when YouTube API is unavailable (e.g., quota exceeded)."""
from datetime import datetime, timedelta
import random
import hashlib

# Expanded demo videos organized by category - MUCH more content
DEMO_VIDEOS = {
    "EDUCATION": [
        {"id": "edu_1", "title": "Python Tutorial for Beginners - Full Course", "channel_title": "Programming with Mosh", "duration_seconds": 3600, "view_count": 15000000, "thumbnail_url": "https://i.ytimg.com/vi/rfscVS0vtbw/hqdefault.jpg"},
        {"id": "edu_2", "title": "Machine Learning Full Course - 12 Hours", "channel_title": "freeCodeCamp", "duration_seconds": 43200, "view_count": 8000000, "thumbnail_url": "https://i.ytimg.com/vi/GwIo3gDZCVQ/hqdefault.jpg"},
        {"id": "edu_3", "title": "Data Science Tutorial for Beginners", "channel_title": "Simplilearn", "duration_seconds": 5400, "view_count": 3500000, "thumbnail_url": "https://i.ytimg.com/vi/ua-CiDNNj30/hqdefault.jpg"},
        {"id": "edu_4", "title": "JavaScript Crash Course For Beginners", "channel_title": "Traversy Media", "duration_seconds": 5760, "view_count": 6200000, "thumbnail_url": "https://i.ytimg.com/vi/hdI2bqOjy3c/hqdefault.jpg"},
        {"id": "edu_5", "title": "React JS Tutorial - Build a Portfolio Website", "channel_title": "Web Dev Simplified", "duration_seconds": 7200, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/I2UBjN5ER4s/hqdefault.jpg"},
        {"id": "edu_6", "title": "Learn TypeScript in 50 Minutes", "channel_title": "Fireship", "duration_seconds": 3000, "view_count": 4500000, "thumbnail_url": "https://i.ytimg.com/vi/ahCwqrYpIuM/hqdefault.jpg"},
        {"id": "edu_7", "title": "Docker Tutorial for Beginners", "channel_title": "TechWorld with Nana", "duration_seconds": 7200, "view_count": 3200000, "thumbnail_url": "https://i.ytimg.com/vi/3c-iBn73dDE/hqdefault.jpg"},
        {"id": "edu_8", "title": "Git and GitHub for Beginners - Crash Course", "channel_title": "freeCodeCamp", "duration_seconds": 5400, "view_count": 5800000, "thumbnail_url": "https://i.ytimg.com/vi/RGOj5yH7evk/hqdefault.jpg"},
        {"id": "edu_9", "title": "SQL Tutorial - Full Database Course for Beginners", "channel_title": "freeCodeCamp", "duration_seconds": 14400, "view_count": 7200000, "thumbnail_url": "https://i.ytimg.com/vi/HXV3zeQKqGY/hqdefault.jpg"},
        {"id": "edu_10", "title": "AWS Tutorial for Beginners", "channel_title": "Simplilearn", "duration_seconds": 10800, "view_count": 2900000, "thumbnail_url": "https://i.ytimg.com/vi/ubCNZRNjhyo/hqdefault.jpg"},
        {"id": "edu_11", "title": "Node.js Full Course for Beginners", "channel_title": "Dave Gray", "duration_seconds": 28800, "view_count": 1500000, "thumbnail_url": "https://i.ytimg.com/vi/f2EqECiTBL8/hqdefault.jpg"},
        {"id": "edu_12", "title": "Vue.js Course for Beginners", "channel_title": "The Net Ninja", "duration_seconds": 14400, "view_count": 1200000, "thumbnail_url": "https://i.ytimg.com/vi/YrxBCBibVo0/hqdefault.jpg"},
        {"id": "edu_13", "title": "Rust Programming Tutorial", "channel_title": "Let's Get Rusty", "duration_seconds": 7200, "view_count": 890000, "thumbnail_url": "https://i.ytimg.com/vi/OX9HJsJUDxA/hqdefault.jpg"},
        {"id": "edu_14", "title": "Go Programming Language Full Course", "channel_title": "Tech With Tim", "duration_seconds": 18000, "view_count": 650000, "thumbnail_url": "https://i.ytimg.com/vi/un6ZyFkqFKo/hqdefault.jpg"},
        {"id": "edu_15", "title": "Kubernetes Tutorial for Beginners", "channel_title": "TechWorld with Nana", "duration_seconds": 14400, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/X48VuDVv0do/hqdefault.jpg"},
        {"id": "edu_16", "title": "C++ Programming Course - Beginner to Advanced", "channel_title": "freeCodeCamp", "duration_seconds": 108000, "view_count": 4300000, "thumbnail_url": "https://i.ytimg.com/vi/8jLOx1hD3_o/hqdefault.jpg"},
        {"id": "edu_17", "title": "Java Programming Tutorial", "channel_title": "Bro Code", "duration_seconds": 43200, "view_count": 3800000, "thumbnail_url": "https://i.ytimg.com/vi/xk4_1vDrzzo/hqdefault.jpg"},
        {"id": "edu_18", "title": "HTML & CSS Full Course for Beginners", "channel_title": "SuperSimpleDev", "duration_seconds": 25200, "view_count": 2500000, "thumbnail_url": "https://i.ytimg.com/vi/G3e-cpL7ofc/hqdefault.jpg"},
        {"id": "edu_19", "title": "Linux Command Line Full Course", "channel_title": "freeCodeCamp", "duration_seconds": 18000, "view_count": 1800000, "thumbnail_url": "https://i.ytimg.com/vi/ZtqBQ68cfJc/hqdefault.jpg"},
        {"id": "edu_20", "title": "MongoDB Tutorial for Beginners", "channel_title": "The Net Ninja", "duration_seconds": 10800, "view_count": 980000, "thumbnail_url": "https://i.ytimg.com/vi/ExcRbA7fy_A/hqdefault.jpg"},
    ],
    "SCIENCE_TECH": [
        {"id": "tech_1", "title": "How Does the Internet Work?", "channel_title": "Lesics", "duration_seconds": 900, "view_count": 4500000, "thumbnail_url": "https://i.ytimg.com/vi/x3c1ih2NJEg/hqdefault.jpg"},
        {"id": "tech_2", "title": "How AI Will Change Everything", "channel_title": "Veritasium", "duration_seconds": 1200, "view_count": 9800000, "thumbnail_url": "https://i.ytimg.com/vi/aircAruvnKk/hqdefault.jpg"},
        {"id": "tech_3", "title": "The Science of 3D Printing", "channel_title": "Stuff Made Here", "duration_seconds": 1800, "view_count": 3200000, "thumbnail_url": "https://i.ytimg.com/vi/n12WjLGzRWM/hqdefault.jpg"},
        {"id": "tech_4", "title": "Quantum Computing Explained", "channel_title": "Kurzgesagt", "duration_seconds": 720, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/JhHMJCUmq28/hqdefault.jpg"},
        {"id": "tech_5", "title": "SpaceX Starship Deep Dive", "channel_title": "Everyday Astronaut", "duration_seconds": 3600, "view_count": 1800000, "thumbnail_url": "https://i.ytimg.com/vi/921VbEMAwwY/hqdefault.jpg"},
        {"id": "tech_6", "title": "How Batteries Work", "channel_title": "Undecided with Matt Ferrell", "duration_seconds": 1500, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/QnrRnYtABkI/hqdefault.jpg"},
        {"id": "tech_7", "title": "The Future of Electric Cars", "channel_title": "MKBHD", "duration_seconds": 1200, "view_count": 8900000, "thumbnail_url": "https://i.ytimg.com/vi/MrUWMg1tMNI/hqdefault.jpg"},
        {"id": "tech_8", "title": "How Nuclear Reactors Work", "channel_title": "Real Engineering", "duration_seconds": 1800, "view_count": 5400000, "thumbnail_url": "https://i.ytimg.com/vi/poPLSgbSO6k/hqdefault.jpg"},
        {"id": "tech_9", "title": "The Science of Black Holes", "channel_title": "PBS Space Time", "duration_seconds": 1200, "view_count": 3800000, "thumbnail_url": "https://i.ytimg.com/vi/e-P5IFTqB98/hqdefault.jpg"},
        {"id": "tech_10", "title": "How CRISPR Gene Editing Works", "channel_title": "Kurzgesagt", "duration_seconds": 600, "view_count": 15000000, "thumbnail_url": "https://i.ytimg.com/vi/jAhjPd4uNFY/hqdefault.jpg"},
        {"id": "tech_11", "title": "Understanding Neural Networks", "channel_title": "3Blue1Brown", "duration_seconds": 1200, "view_count": 8500000, "thumbnail_url": "https://i.ytimg.com/vi/aircAruvnKk/hqdefault.jpg"},
        {"id": "tech_12", "title": "The James Webb Telescope Explained", "channel_title": "Astrum", "duration_seconds": 2400, "view_count": 2300000, "thumbnail_url": "https://i.ytimg.com/vi/aICaAEXDJQQ/hqdefault.jpg"},
        {"id": "tech_13", "title": "How Does GPS Work?", "channel_title": "Practical Engineering", "duration_seconds": 900, "view_count": 4100000, "thumbnail_url": "https://i.ytimg.com/vi/FU_pY2sTwTA/hqdefault.jpg"},
        {"id": "tech_14", "title": "The Science of Climate Change", "channel_title": "It's Okay To Be Smart", "duration_seconds": 1500, "view_count": 1900000, "thumbnail_url": "https://i.ytimg.com/vi/SDxufRrhqGo/hqdefault.jpg"},
        {"id": "tech_15", "title": "How Fusion Energy Works", "channel_title": "Kyle Hill", "duration_seconds": 1800, "view_count": 1200000, "thumbnail_url": "https://i.ytimg.com/vi/mZsaaturR6E/hqdefault.jpg"},
        {"id": "tech_16", "title": "Explaining Blockchain Technology", "channel_title": "Simply Explained", "duration_seconds": 600, "view_count": 3400000, "thumbnail_url": "https://i.ytimg.com/vi/SSo_EIwHSd4/hqdefault.jpg"},
        {"id": "tech_17", "title": "How Modern CPUs Work", "channel_title": "Linus Tech Tips", "duration_seconds": 1200, "view_count": 6700000, "thumbnail_url": "https://i.ytimg.com/vi/vqs_0W-MSB0/hqdefault.jpg"},
        {"id": "tech_18", "title": "The Physics of Time Travel", "channel_title": "Veritasium", "duration_seconds": 1800, "view_count": 11000000, "thumbnail_url": "https://i.ytimg.com/vi/O2jkV4BsN6U/hqdefault.jpg"},
        {"id": "tech_19", "title": "How mRNA Vaccines Work", "channel_title": "SciShow", "duration_seconds": 900, "view_count": 2800000, "thumbnail_url": "https://i.ytimg.com/vi/XPeeCyJReZw/hqdefault.jpg"},
        {"id": "tech_20", "title": "The Future of Solar Power", "channel_title": "Undecided with Matt Ferrell", "duration_seconds": 1200, "view_count": 1500000, "thumbnail_url": "https://i.ytimg.com/vi/N-yALPEpV4w/hqdefault.jpg"},
    ],
    "HOWTO_STYLE": [
        {"id": "howto_1", "title": "How to Cook Perfect Pasta Every Time", "channel_title": "Gordon Ramsay", "duration_seconds": 600, "view_count": 8500000, "thumbnail_url": "https://i.ytimg.com/vi/UYhKDweME3A/hqdefault.jpg"},
        {"id": "howto_2", "title": "Home Workout - No Equipment Needed", "channel_title": "THENX", "duration_seconds": 1200, "view_count": 4200000, "thumbnail_url": "https://i.ytimg.com/vi/vc1E5CfRfos/hqdefault.jpg"},
        {"id": "howto_3", "title": "DIY Room Makeover on a Budget", "channel_title": "Mr. Kate", "duration_seconds": 1800, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/2V6_LNzlNOk/hqdefault.jpg"},
        {"id": "howto_4", "title": "Productivity Tips from a CEO", "channel_title": "Ali Abdaal", "duration_seconds": 900, "view_count": 3800000, "thumbnail_url": "https://i.ytimg.com/vi/A2sS00egAzg/hqdefault.jpg"},
        {"id": "howto_5", "title": "Learn Guitar in 21 Days", "channel_title": "Justin Guitar", "duration_seconds": 2400, "view_count": 5500000, "thumbnail_url": "https://i.ytimg.com/vi/BBz-Jyr23M4/hqdefault.jpg"},
        {"id": "howto_6", "title": "Morning Routine for Success", "channel_title": "Thomas Frank", "duration_seconds": 720, "view_count": 2300000, "thumbnail_url": "https://i.ytimg.com/vi/ysR-6wJXvHM/hqdefault.jpg"},
        {"id": "howto_7", "title": "How to Start a Business", "channel_title": "Graham Stephan", "duration_seconds": 1800, "view_count": 4100000, "thumbnail_url": "https://i.ytimg.com/vi/pt8VYOfr8To/hqdefault.jpg"},
        {"id": "howto_8", "title": "Photography Tips for Beginners", "channel_title": "Peter McKinnon", "duration_seconds": 1200, "view_count": 3600000, "thumbnail_url": "https://i.ytimg.com/vi/LxO-6rlihSg/hqdefault.jpg"},
        {"id": "howto_9", "title": "How to Edit Videos Like a Pro", "channel_title": "MKBHD", "duration_seconds": 900, "view_count": 5200000, "thumbnail_url": "https://i.ytimg.com/vi/O6ERELse_QY/hqdefault.jpg"},
        {"id": "howto_10", "title": "Beginner's Guide to Investing", "channel_title": "Andrei Jikh", "duration_seconds": 1500, "view_count": 2800000, "thumbnail_url": "https://i.ytimg.com/vi/gFQNPmLKj1k/hqdefault.jpg"},
        {"id": "howto_11", "title": "Home Cooking Essentials", "channel_title": "Joshua Weissman", "duration_seconds": 1800, "view_count": 3100000, "thumbnail_url": "https://i.ytimg.com/vi/qWAagS_MANg/hqdefault.jpg"},
        {"id": "howto_12", "title": "How to Build Good Habits", "channel_title": "Improvement Pill", "duration_seconds": 600, "view_count": 4500000, "thumbnail_url": "https://i.ytimg.com/vi/W1eYrhGeffc/hqdefault.jpg"},
        {"id": "howto_13", "title": "Meditation for Beginners", "channel_title": "Headspace", "duration_seconds": 900, "view_count": 2700000, "thumbnail_url": "https://i.ytimg.com/vi/thcEuMDWxoI/hqdefault.jpg"},
        {"id": "howto_14", "title": "How to Design Your Home", "channel_title": "Havenly", "duration_seconds": 1200, "view_count": 1800000, "thumbnail_url": "https://i.ytimg.com/vi/4ERbbJWlhgI/hqdefault.jpg"},
        {"id": "howto_15", "title": "Budget Travel Tips", "channel_title": "Kara and Nate", "duration_seconds": 1500, "view_count": 2400000, "thumbnail_url": "https://i.ytimg.com/vi/Ep0yLMjGkRE/hqdefault.jpg"},
        {"id": "howto_16", "title": "Drawing Tutorial for Beginners", "channel_title": "Proko", "duration_seconds": 2400, "view_count": 1900000, "thumbnail_url": "https://i.ytimg.com/vi/1EPNYWeEf1U/hqdefault.jpg"},
        {"id": "howto_17", "title": "How to Study Effectively", "channel_title": "Mike and Matty", "duration_seconds": 720, "view_count": 3200000, "thumbnail_url": "https://i.ytimg.com/vi/ukLnPbIffxE/hqdefault.jpg"},
        {"id": "howto_18", "title": "Yoga for Complete Beginners", "channel_title": "Yoga With Adriene", "duration_seconds": 1800, "view_count": 8900000, "thumbnail_url": "https://i.ytimg.com/vi/v7AYKMP6rOE/hqdefault.jpg"},
        {"id": "howto_19", "title": "Skincare Routine Guide", "channel_title": "James Welsh", "duration_seconds": 900, "view_count": 1500000, "thumbnail_url": "https://i.ytimg.com/vi/OrElyY7MFVs/hqdefault.jpg"},
        {"id": "howto_20", "title": "How to Learn Any Skill Fast", "channel_title": "Matt D'Avella", "duration_seconds": 1200, "view_count": 4800000, "thumbnail_url": "https://i.ytimg.com/vi/5MgBikgcWnY/hqdefault.jpg"},
    ],
    "MUSIC": [
        {"id": "music_1", "title": "Lofi Hip Hop Radio - Beats to Study/Relax to", "channel_title": "Lofi Girl", "duration_seconds": 0, "view_count": 950000000, "thumbnail_url": "https://i.ytimg.com/vi/jfKfPfyJRdk/hqdefault.jpg"},
        {"id": "music_2", "title": "Classical Music Playlist for Concentration", "channel_title": "HALIDONMUSIC", "duration_seconds": 10800, "view_count": 45000000, "thumbnail_url": "https://i.ytimg.com/vi/mIYzp5rcTvU/hqdefault.jpg"},
        {"id": "music_3", "title": "Jazz Music for Work and Study", "channel_title": "Cafe Music BGM", "duration_seconds": 7200, "view_count": 28000000, "thumbnail_url": "https://i.ytimg.com/vi/fEvM-OUbaKs/hqdefault.jpg"},
        {"id": "music_4", "title": "Piano Music for Relaxation", "channel_title": "Relaxing Records", "duration_seconds": 3600, "view_count": 18000000, "thumbnail_url": "https://i.ytimg.com/vi/77ZozI0rw7w/hqdefault.jpg"},
        {"id": "music_5", "title": "Best Pop Songs 2024 Playlist", "channel_title": "Top Music", "duration_seconds": 5400, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/kXYiU_JCYtU/hqdefault.jpg"},
        {"id": "music_6", "title": "Ambient Music for Sleep", "channel_title": "Yellow Brick Cinema", "duration_seconds": 28800, "view_count": 89000000, "thumbnail_url": "https://i.ytimg.com/vi/lFcSrYw-ARY/hqdefault.jpg"},
        {"id": "music_7", "title": "Epic Orchestral Music Mix", "channel_title": "HDSounDI", "duration_seconds": 7200, "view_count": 34000000, "thumbnail_url": "https://i.ytimg.com/vi/d4PSHHNB0EY/hqdefault.jpg"},
        {"id": "music_8", "title": "Acoustic Guitar Relaxing Music", "channel_title": "Acoustic FM", "duration_seconds": 10800, "view_count": 21000000, "thumbnail_url": "https://i.ytimg.com/vi/T2K-MAdBJTo/hqdefault.jpg"},
        {"id": "music_9", "title": "Electronic Dance Music Mix", "channel_title": "NCS Release", "duration_seconds": 3600, "view_count": 156000000, "thumbnail_url": "https://i.ytimg.com/vi/bM7SZ5SBzyY/hqdefault.jpg"},
        {"id": "music_10", "title": "Chill Indie Pop Playlist", "channel_title": "Indie Supreme", "duration_seconds": 5400, "view_count": 8900000, "thumbnail_url": "https://i.ytimg.com/vi/3jWRrafhO7M/hqdefault.jpg"},
        {"id": "music_11", "title": "Deep House Mix for Focus", "channel_title": "Chill Nation", "duration_seconds": 7200, "view_count": 42000000, "thumbnail_url": "https://i.ytimg.com/vi/5qap5aO4i9A/hqdefault.jpg"},
        {"id": "music_12", "title": "Meditation Music - 1 Hour", "channel_title": "Soothing Relaxation", "duration_seconds": 3600, "view_count": 67000000, "thumbnail_url": "https://i.ytimg.com/vi/1ZYbU82GVz4/hqdefault.jpg"},
        {"id": "music_13", "title": "Rock Classics Playlist", "channel_title": "Rock Legends", "duration_seconds": 14400, "view_count": 23000000, "thumbnail_url": "https://i.ytimg.com/vi/1w7OgIMMRc4/hqdefault.jpg"},
        {"id": "music_14", "title": "R&B Soul Mix 2024", "channel_title": "Chill R&B", "duration_seconds": 5400, "view_count": 15000000, "thumbnail_url": "https://i.ytimg.com/vi/e3L1PIY1pN8/hqdefault.jpg"},
        {"id": "music_15", "title": "Nature Sounds - Rain and Thunder", "channel_title": "Relaxing White Noise", "duration_seconds": 36000, "view_count": 112000000, "thumbnail_url": "https://i.ytimg.com/vi/nMfPqeZjc2c/hqdefault.jpg"},
        {"id": "music_16", "title": "Hip Hop Workout Music", "channel_title": "Workout Music Service", "duration_seconds": 3600, "view_count": 18000000, "thumbnail_url": "https://i.ytimg.com/vi/6OVQv6wIpfg/hqdefault.jpg"},
        {"id": "music_17", "title": "Country Music Hits 2024", "channel_title": "Country Now", "duration_seconds": 7200, "view_count": 9500000, "thumbnail_url": "https://i.ytimg.com/vi/QfcLcDBII78/hqdefault.jpg"},
        {"id": "music_18", "title": "K-Pop Hits Playlist", "channel_title": "K-Pop Universe", "duration_seconds": 5400, "view_count": 78000000, "thumbnail_url": "https://i.ytimg.com/vi/UOxkGD8qRB4/hqdefault.jpg"},
        {"id": "music_19", "title": "Latin Dance Music Mix", "channel_title": "Latin Vibes", "duration_seconds": 3600, "view_count": 34000000, "thumbnail_url": "https://i.ytimg.com/vi/kJQP7kiw5Fk/hqdefault.jpg"},
        {"id": "music_20", "title": "Reggae Vibes Playlist", "channel_title": "Reggae Camp", "duration_seconds": 7200, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/wWF8ZZrI0H0/hqdefault.jpg"},
    ],
    "GAMING": [
        {"id": "game_1", "title": "Best Gaming Moments of 2024", "channel_title": "GameSpot", "duration_seconds": 1200, "view_count": 5600000, "thumbnail_url": "https://i.ytimg.com/vi/xvFZjo5PgG0/hqdefault.jpg"},
        {"id": "game_2", "title": "Minecraft Hardcore Survival Series", "channel_title": "Dream", "duration_seconds": 2400, "view_count": 35000000, "thumbnail_url": "https://i.ytimg.com/vi/u9WtpyqRGbo/hqdefault.jpg"},
        {"id": "game_3", "title": "GTA 6 Trailer Analysis", "channel_title": "IGN", "duration_seconds": 900, "view_count": 28000000, "thumbnail_url": "https://i.ytimg.com/vi/QdBZY2fkU-0/hqdefault.jpg"},
        {"id": "game_4", "title": "Pro Tips for Valorant Beginners", "channel_title": "100 Thieves", "duration_seconds": 1500, "view_count": 4200000, "thumbnail_url": "https://i.ytimg.com/vi/5p3I_4EV4ZY/hqdefault.jpg"},
        {"id": "game_5", "title": "Elden Ring Boss Guide", "channel_title": "VaatiVidya", "duration_seconds": 1800, "view_count": 8900000, "thumbnail_url": "https://i.ytimg.com/vi/K_03kFqWfqs/hqdefault.jpg"},
        {"id": "game_6", "title": "Fortnite Tips and Tricks", "channel_title": "Ninja", "duration_seconds": 1200, "view_count": 15000000, "thumbnail_url": "https://i.ytimg.com/vi/jqFSW9xCUzU/hqdefault.jpg"},
        {"id": "game_7", "title": "Call of Duty Warzone Strategy Guide", "channel_title": "JGOD", "duration_seconds": 1800, "view_count": 3400000, "thumbnail_url": "https://i.ytimg.com/vi/R6wMB9k_uOg/hqdefault.jpg"},
        {"id": "game_8", "title": "League of Legends Pro Tips", "channel_title": "Faker", "duration_seconds": 2400, "view_count": 8700000, "thumbnail_url": "https://i.ytimg.com/vi/rRzxEiBLQCA/hqdefault.jpg"},
        {"id": "game_9", "title": "Zelda Tears of the Kingdom Secrets", "channel_title": "Nintendo Life", "duration_seconds": 1500, "view_count": 6200000, "thumbnail_url": "https://i.ytimg.com/vi/uHGShqcAHlQ/hqdefault.jpg"},
        {"id": "game_10", "title": "Hogwarts Legacy Complete Walkthrough", "channel_title": "GameRanx", "duration_seconds": 7200, "view_count": 4500000, "thumbnail_url": "https://i.ytimg.com/vi/1O6Qstncpnc/hqdefault.jpg"},
        {"id": "game_11", "title": "FIFA 24 Ultimate Team Guide", "channel_title": "Nepenthez", "duration_seconds": 1800, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"},
        {"id": "game_12", "title": "Among Us Strategies", "channel_title": "Disguised Toast", "duration_seconds": 1200, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/kCJvNMPAsvY/hqdefault.jpg"},
        {"id": "game_13", "title": "Cyberpunk 2077 Build Guide", "channel_title": "Fextralife", "duration_seconds": 2100, "view_count": 3800000, "thumbnail_url": "https://i.ytimg.com/vi/UnA7tepsc7s/hqdefault.jpg"},
        {"id": "game_14", "title": "Spider-Man 2 PS5 Gameplay", "channel_title": "PlayStation", "duration_seconds": 900, "view_count": 18000000, "thumbnail_url": "https://i.ytimg.com/vi/nq1M_Wc4FIc/hqdefault.jpg"},
        {"id": "game_15", "title": "Starfield Exploration Guide", "channel_title": "Bethesda", "duration_seconds": 1800, "view_count": 5600000, "thumbnail_url": "https://i.ytimg.com/vi/pYqyVpCV-3c/hqdefault.jpg"},
        {"id": "game_16", "title": "Baldur's Gate 3 Class Guide", "channel_title": "Larian Studios", "duration_seconds": 2400, "view_count": 4200000, "thumbnail_url": "https://i.ytimg.com/vi/1T22wNvoNiU/hqdefault.jpg"},
        {"id": "game_17", "title": "Apex Legends Movement Guide", "channel_title": "Aceu", "duration_seconds": 1500, "view_count": 2900000, "thumbnail_url": "https://i.ytimg.com/vi/GKq6WfpEdBI/hqdefault.jpg"},
        {"id": "game_18", "title": "Palworld Beginner's Guide", "channel_title": "Arekkz Gaming", "duration_seconds": 1800, "view_count": 7800000, "thumbnail_url": "https://i.ytimg.com/vi/qLCAK83fVOc/hqdefault.jpg"},
        {"id": "game_19", "title": "Final Fantasy XVI Review", "channel_title": "SkillUp", "duration_seconds": 2700, "view_count": 1500000, "thumbnail_url": "https://i.ytimg.com/vi/mWBTdj6sLkA/hqdefault.jpg"},
        {"id": "game_20", "title": "Diablo 4 Endgame Guide", "channel_title": "Rhykker", "duration_seconds": 2100, "view_count": 2300000, "thumbnail_url": "https://i.ytimg.com/vi/BibhFSqWL0I/hqdefault.jpg"},
    ],
    "ENTERTAINMENT": [
        {"id": "ent_1", "title": "Top 10 Movies of 2024", "channel_title": "WatchMojo", "duration_seconds": 1200, "view_count": 7800000, "thumbnail_url": "https://i.ytimg.com/vi/w7ejDZ8SWv8/hqdefault.jpg"},
        {"id": "ent_2", "title": "Stand-Up Comedy Special", "channel_title": "Netflix Comedy", "duration_seconds": 3600, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/0ZBD2tcKZak/hqdefault.jpg"},
        {"id": "ent_3", "title": "Travel Vlog: Japan 2024", "channel_title": "Lost LeBlanc", "duration_seconds": 1800, "view_count": 4500000, "thumbnail_url": "https://i.ytimg.com/vi/FyU1a4c1Tdk/hqdefault.jpg"},
        {"id": "ent_4", "title": "Celebrity Interview Collection", "channel_title": "The Tonight Show", "duration_seconds": 2700, "view_count": 9200000, "thumbnail_url": "https://i.ytimg.com/vi/4SVaHxJhTmk/hqdefault.jpg"},
        {"id": "ent_5", "title": "Animation Short Film Compilation", "channel_title": "CGMeetup", "duration_seconds": 1500, "view_count": 3800000, "thumbnail_url": "https://i.ytimg.com/vi/skV-q5KjrUA/hqdefault.jpg"},
        {"id": "ent_6", "title": "Best TV Shows 2024", "channel_title": "CineFix", "duration_seconds": 1800, "view_count": 5600000, "thumbnail_url": "https://i.ytimg.com/vi/t3217H8JppI/hqdefault.jpg"},
        {"id": "ent_7", "title": "Hidden Gems on Netflix", "channel_title": "MovieFlame", "duration_seconds": 1200, "view_count": 3200000, "thumbnail_url": "https://i.ytimg.com/vi/Eas5bH-07QE/hqdefault.jpg"},
        {"id": "ent_8", "title": "Behind the Scenes: Marvel Movies", "channel_title": "Marvel Entertainment", "duration_seconds": 900, "view_count": 18000000, "thumbnail_url": "https://i.ytimg.com/vi/TcMBFSGVi1c/hqdefault.jpg"},
        {"id": "ent_9", "title": "Oscar Winners Best Speeches", "channel_title": "Oscars", "duration_seconds": 2100, "view_count": 8400000, "thumbnail_url": "https://i.ytimg.com/vi/GNjpxdqJWOY/hqdefault.jpg"},
        {"id": "ent_10", "title": "True Crime Documentary", "channel_title": "Netflix", "duration_seconds": 5400, "view_count": 15000000, "thumbnail_url": "https://i.ytimg.com/vi/8WKgAkpBYGI/hqdefault.jpg"},
        {"id": "ent_11", "title": "Broadway Musicals Best Moments", "channel_title": "Broadway HD", "duration_seconds": 1800, "view_count": 2100000, "thumbnail_url": "https://i.ytimg.com/vi/MpYGVEpz56U/hqdefault.jpg"},
        {"id": "ent_12", "title": "Food Challenge: 24 Hours", "channel_title": "MrBeast", "duration_seconds": 1200, "view_count": 89000000, "thumbnail_url": "https://i.ytimg.com/vi/TQHEJj68Jew/hqdefault.jpg"},
        {"id": "ent_13", "title": "World's Most Amazing Places", "channel_title": "Beautiful Destinations", "duration_seconds": 600, "view_count": 34000000, "thumbnail_url": "https://i.ytimg.com/vi/xSWGUVoDHvs/hqdefault.jpg"},
        {"id": "ent_14", "title": "Funny Animal Compilation", "channel_title": "The Pet Collective", "duration_seconds": 900, "view_count": 56000000, "thumbnail_url": "https://i.ytimg.com/vi/MuJt4uLlT7g/hqdefault.jpg"},
        {"id": "ent_15", "title": "Extreme Sports Compilation", "channel_title": "Red Bull", "duration_seconds": 1500, "view_count": 23000000, "thumbnail_url": "https://i.ytimg.com/vi/JELm-y8lMb4/hqdefault.jpg"},
        {"id": "ent_16", "title": "Magic Tricks Revealed", "channel_title": "Penn & Teller", "duration_seconds": 1800, "view_count": 12000000, "thumbnail_url": "https://i.ytimg.com/vi/8osRaFTtgHo/hqdefault.jpg"},
        {"id": "ent_17", "title": "Talent Show Best Auditions", "channel_title": "Got Talent Global", "duration_seconds": 2400, "view_count": 67000000, "thumbnail_url": "https://i.ytimg.com/vi/POLPxzP2BNg/hqdefault.jpg"},
        {"id": "ent_18", "title": "World Records Being Broken", "channel_title": "Guinness World Records", "duration_seconds": 1200, "view_count": 45000000, "thumbnail_url": "https://i.ytimg.com/vi/a6WnRBsOIl8/hqdefault.jpg"},
        {"id": "ent_19", "title": "Satisfying Video Compilation", "channel_title": "Oddly Satisfying", "duration_seconds": 600, "view_count": 78000000, "thumbnail_url": "https://i.ytimg.com/vi/7UH2j4vLWas/hqdefault.jpg"},
        {"id": "ent_20", "title": "Prank Wars Compilation", "channel_title": "Dude Perfect", "duration_seconds": 1500, "view_count": 34000000, "thumbnail_url": "https://i.ytimg.com/vi/bpyX5E1tARY/hqdefault.jpg"},
    ],
}

# Page tracking for pagination
_page_state = {}

def get_demo_videos(categories=None, max_results=20, page_token=None):
    """Get demo videos, optionally filtered by categories, with pagination support."""
    all_videos = []
    
    if categories:
        # Get videos from specified categories with their category label
        for cat in categories:
            if cat in DEMO_VIDEOS:
                for video in DEMO_VIDEOS[cat]:
                    video_copy = dict(video)
                    video_copy["category"] = cat  # Add category field
                    all_videos.append(video_copy)
    else:
        # Get videos from all categories with their category labels
        for cat, videos in DEMO_VIDEOS.items():
            for video in videos:
                video_copy = dict(video)
                video_copy["category"] = cat  # Add category field
                all_videos.append(video_copy)
    
    # Add common fields
    now = datetime.utcnow()
    for i, video in enumerate(all_videos):
        # Create unique ID with random suffix for pagination
        base_id = video.get("id", f"video_{i}")
        video["id"] = f"{base_id}_{random.randint(1000, 9999)}"
        video["is_short"] = video.get("duration_seconds", 0) < 60
        video["published_at"] = (now - timedelta(days=random.randint(1, 365))).isoformat() + "Z"
        if not video.get("thumbnail_url"):
            video["thumbnail_url"] = f"https://via.placeholder.com/320x180?text={video['title'][:20]}"
        # Add default scores for fast filtering
        video["clickbait_score"] = 0.1
        video["entertainment_score"] = 0.3 if video.get("category") in ["EDUCATION", "SCIENCE_TECH"] else 0.6
    
    # Shuffle for random order
    random.shuffle(all_videos)
    
    return all_videos[:max_results]


def generate_dynamic_videos(categories=None, count=50, seed=None):
    """Generate dynamic video content for infinite scrolling."""
    if seed:
        random.seed(seed)
    
    # Base video templates for generating variety
    templates = {
        "EDUCATION": [
            "{topic} Tutorial for Beginners", 
            "Learn {topic} in {time}", 
            "{topic} Full Course",
            "Master {topic} Step by Step",
            "{topic} Complete Guide",
            "Introduction to {topic}",
            "{topic} Crash Course",
            "Advanced {topic} Techniques",
            "{topic} Tips and Tricks",
            "{topic} Best Practices"
        ],
        "SCIENCE_TECH": [
            "How {tech} Works",
            "The Science of {topic}",
            "{tech} Explained Simply",
            "The Future of {tech}",
            "{topic} Deep Dive",
            "Understanding {topic}",
            "{tech} vs {alt_tech}",
            "Why {tech} Matters",
            "{topic} Revolution",
            "Inside {tech}"
        ],
        "NEWS_POLITICS": [
            "Breaking: {topic} Update {year}",
            "Analysis: The {topic} Situation",
            "Daily News Roundup: {topic}",
            "What's Happening with {topic}",
            "{topic}: Expert Analysis",
            "Current Events: {topic} Report",
            "Weekly News: {topic} Updates",
            "{topic} News Explained",
            "Top Stories: {topic} Today",
            "News Brief: {topic} Summary"
        ],
        "HOWTO_STYLE": [
            "How to {action} - Complete Guide",
            "{action} Tips for Beginners",
            "DIY {project} Tutorial",
            "Easy Ways to {action}",
            "{action} Step by Step",
            "Quick {action} Tutorial",
            "Best {action} Techniques",
            "Beginner's Guide to {action}",
            "{action} Made Simple",
            "Pro Tips for {action}"
        ],
        "MUSIC": [
            "{genre} Music for {activity}",
            "{mood} {genre} Playlist",
            "Best {genre} Hits {year}",
            "{genre} Mix - {duration}",
            "Relaxing {genre} Music",
            "{genre} Vibes",
            "{mood} Songs Playlist",
            "{genre} for Focus",
            "Chill {genre} Mix",
            "{genre} Essentials"
        ],
        "GAMING": [
            "{game} Gameplay - Full Walkthrough",
            "{game} Tips and Tricks",
            "Best {game} Strategies",
            "{game} Pro Guide",
            "{game} for Beginners",
            "{game} Stream Highlights",
            "{game} Epic Moments",
            "{game} Tutorial",
            "{game} Ranked Guide",
            "{game} Review {year}"
        ],
        "ENTERTAINMENT": [
            "Top 10 {topic} Moments",
            "Best of {topic} {year}",
            "{topic} Compilation",
            "Amazing {topic} Stories",
            "{topic} Documentary",
            "{topic} Behind the Scenes",
            "Incredible {topic} Facts",
            "{topic} Highlights",
            "Epic {topic} Moments",
            "{topic} Review"
        ],
    }
    
    topics = ["Python", "JavaScript", "React", "Machine Learning", "AI", "Data Science", 
              "Web Development", "Mobile Apps", "Cloud Computing", "DevOps", "Cybersecurity"]
    techs = ["Quantum Computing", "Blockchain", "5G", "IoT", "VR", "AR", "Robotics", "Drones"]
    genres = ["Lofi", "Jazz", "Classical", "Electronic", "Ambient", "Pop", "Rock", "Hip Hop"]
    moods = ["Chill", "Upbeat", "Relaxing", "Energetic", "Peaceful", "Happy"]
    activities = ["Study", "Work", "Sleep", "Focus", "Meditation", "Coding", "Reading"]
    actions = ["Cook", "Build", "Create", "Design", "Organize", "Clean", "Decorate", "Fix"]
    projects = ["Furniture", "Garden", "Room Decor", "Storage", "Kitchen", "Office", "Workshop"]
    games = ["Minecraft", "Fortnite", "Valorant", "GTA", "Elden Ring", "Zelda", "Mario", "Pokemon"]
    channels = ["TechMaster", "CodeAcademy", "ScienceHub", "MusicVibes", "LearnDaily", 
                "DigitalNomad", "StudyBuddy", "FutureTech", "ChillBeats", "EduPro",
                "NewsToday", "GamePro", "DIYMaster", "TopNews", "EntertainNow"]
    
    generated = []
    
    # Filter to only categories we have templates for
    available_cats = [c for c in (categories or list(DEMO_VIDEOS.keys())) 
                      if c in templates]
    if not available_cats:
        available_cats = ["EDUCATION"]  # Fallback
    
    for i in range(count):
        # Cycle through categories evenly
        cat = available_cats[i % len(available_cats)]
        
        title_templates = templates.get(cat, templates["EDUCATION"])
        title = random.choice(title_templates)
        
        # Fill in placeholders
        title = title.replace("{topic}", random.choice(topics))
        title = title.replace("{tech}", random.choice(techs))
        title = title.replace("{alt_tech}", random.choice(techs))
        title = title.replace("{genre}", random.choice(genres))
        title = title.replace("{mood}", random.choice(moods))
        title = title.replace("{activity}", random.choice(activities))
        title = title.replace("{action}", random.choice(actions))
        title = title.replace("{project}", random.choice(projects))
        title = title.replace("{game}", random.choice(games))
        title = title.replace("{time}", random.choice(["1 Hour", "30 Minutes", "2 Hours"]))
        title = title.replace("{duration}", random.choice(["1 Hour Mix", "2 Hour Session"]))
        title = title.replace("{year}", "2024")
        
        video = {
            "id": f"gen_{hashlib.md5(f'{i}{random.random()}'.encode()).hexdigest()[:10]}",
            "title": title,
            "channel_title": random.choice(channels),
            "duration_seconds": random.randint(300, 7200),
            "view_count": random.randint(100000, 50000000),
            "thumbnail_url": f"https://picsum.photos/seed/{i}/320/180",
            "is_short": False,
            "published_at": (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat() + "Z",
            "category": cat,  # Add category for fast filtering
            "clickbait_score": 0.1,
            "entertainment_score": 0.3 if cat in ["EDUCATION", "SCIENCE_TECH"] else 0.6,
        }
        generated.append(video)
    
    # Reset random seed
    random.seed()
    
    return generated
