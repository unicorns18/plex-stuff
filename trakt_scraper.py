import requests

# listname = "r-rated-action-films"
# headers = {
#   'Content-Type': 'application/json',
#   'trakt-api-version': '2',
#   'trakt-api-key': '3f6bad0655f06b961a185e888a633bcb3702ecdd9e68e44167106420ed62a349'
# }
# list_id = "r-rated-action-films"
# url = f"https://api.trakt.tv/lists/{list_id}/items/movie"
# response = requests.get(url, headers=headers).json()
# titles = []

# for item in response:
#     title = item['movie']['title']
#     imdb_id = item['movie']['ids']['imdb']
#     print(title, imdb_id)
#     titles.append(title)

#titles = ['Seven Samurai', 'Harakiri', 'Yojimbo', 'Ran', 'Rififi', 'North by Northwest', 'Evangelion: 3.0+1.0 Thrice Upon a Time', 'Safety Last!', 'Sherlock Jr.', 'The General', 'Oldboy', 'Aliens', 'Mad Max: Fury Road', 'The Wild Bunch', 'Platoon', 'The Hidden Fortress', 'Aguirre, the Wrath of God', 'Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train', 'Sanjuro', 'Stagecoach', 'Neon Genesis Evangelion: The End of Evangelion', 'The French Connection', 'Terminator 2: Judgment Day', 'Children of Men', 'The Terminator', 'A Trip to the Moon', 'RRR', 'Everything Everywhere All at Once', 'John Wick: Chapter 4', 'Touching the Void', 'Letters from Iwo Jima', 'Heat', 'Kill Bill: Vol. 2', 'Riders of Justice', 'Scarface', 'Logan', 'Bacurau', 'White Heat', 'Bonnie and Clyde', 'The Killer', 'The Man from Nowhere', 'Cell 211', 'Kill Bill: Vol. 1', 'Blade Runner', 'The Matrix', 'Justice League Dark: Apokolips War', 'Bob le Flambeur', 'Love Exposure', "No Man's Land", 'Fist of Legend', 'Hard Boiled', 'A Bittersweet Life', 'Key Largo', 'Lady Snowblood', 'Brother', 'United 93', 'Hot Fuzz', 'The Thief of Bagdad', 'A Night to Remember', 'The Great Silence', 'Scarface', 'A Fistful of Dollars', 'Diva', 'Sin Nombre', 'Infernal Affairs', '13 Assassins', 'Akira', 'Ghost in the Shell', 'Blade Runner 2049', 'Baby Driver', '3:10 to Yuma', 'Drive', 'Zulu', 'To Live and Die in L.A.', '1917', 'John Wick: Chapter 3 - Parabellum', 'Steamboat Bill, Jr.', 'Sonatine', 'Sholay', 'Fallen Angels', 'Sword of the Stranger', 'Ninja Scroll', 'Midnight Run', 'Enter the Dragon', 'Elite Squad: The Enemy Within', 'Dirty Harry', 'Kung Fu Hustle', 'Mad Max 2', 'Train to Busan', 'The 36th Chamber of Shaolin', 'The Legend of Drunken Master', 'Pusher II', "Winchester '73", 'Battle Royale', 'Speed', 'Braveheart', 'The Magnificent Seven', 'Die Hard', 'Black Hawk Down', 'The Witch: Part 1. The Subversion', 'John Wick: Chapter 2', "Mortal Kombat Legends: Scorpion's Revenge", 'Raazi', 'Captain Blood', 'Bring Me the Head of Alfredo Garcia', 'A Better Tomorrow', 'The Taking of Pelham One Two Three', "Knockin' on Heaven's Door", 'Assault on Precinct 13', 'Bāhubali: The Beginning', 'Headhunters', 'Run Lola Run', 'The Crow', 'End of Watch', 'Lethal Weapon', 'Sin City', 'District 9', 'Sicario', 'The Revenant', 'Soorarai Pottru', 'Batman: The Long Halloween, Part Two', 'The Harder They Fall', 'A History of Violence', 'Joint Security Area', 'Zatoichi', 'Lock, Stock and Two Smoking Barrels', 'True Romance', 'The Train', 'Collateral', 'Thief', 'Léon: The Professional', 'Jackass Forever', 'A Taxi Driver', 'The Court Jester', 'The Guns of Navarone', 'The Ballad of Cable Hogue', 'Hera Pheri', 'Haider', 'Drug War', "King of Devil's Island", 'The Age of Shadows', 'Tae Guk Gi: The Brotherhood of War', 'Berserk: The Golden Age Arc III - The Advent', 'Phineas and Ferb: The Movie: Across the 2nd Dimension', 'The Guard', 'I Saw the Devil', 'Three Kings', 'Munich', 'The Last of the Mohicans', 'Ip Man', 'Looper', 'Kantara', 'Ponniyin Selvan: Part II', 'Old Henry', 'Prey', 'All Quiet on the Western Front', 'The Dirty Dozen', 'RoboCop', 'Ip Man 2', 'The Fighter', 'No Way Out', 'Nobody', 'The Witcher: Nightmare of the Wolf', 'Brawl in Cell Block 99', 'El Camino: A Breaking Bad Movie', 'Foreign Correspondent', 'Django', 'El Topo', 'May God Save Us', 'Mesrine: Killer Instinct', 'Evangelion: 2.0 You Can (Not) Advance', 'In the Line of Fire', "'71", 'Crimson Tide', 'Kung Fury', 'Snowpiercer', 'Zombieland', 'V for Vendetta', 'Gladiator', "Zack Snyder's Justice League", 'The Dam Busters', 'The Great Train Robbery', 'Tekkonkinkreet', 'The Blues Brothers', 'Training Day', 'The Suicide Squad', 'Ip Man 4: The Finale', 'Upgrade', 'Bullet in the Head', 'A Touch of Sin', 'Riki-Oh: The Story of Ricky', 'A Wednesday!', 'Runaway Train', 'The Day of the Beast', 'Get Carter', 'Mesrine: Public Enemy #1', 'Rurouni Kenshin Part III: The Legend Ends', 'Berserk: The Golden Age Arc II - The Battle for Doldrey', 'The Proposition', 'Red Cliff', 'Repo Man', 'Marshland', 'Open Range', 'Cowboy Bebop: The Movie', 'Grindhouse', 'Layer Cake', 'First Blood', 'Face/Off', 'Eye in the Sky', 'Total Recall', 'Predestination', 'Rush', 'John Wick', 'The Memory of a Killer', 'The Last Duel', 'The Unbearable Weight of Massive Talent', 'Udta Punjab', 'Deadpool', 'Extreme Job', 'Uri: The Surgical Strike', 'Kaithi', 'Gun Crazy', 'Days of Glory', 'Deep Cover', 'Once Upon a Time in China II', 'Pusher 3', 'Bhaag Milkha Bhaag', '36th Precinct', 'Infernal Affairs II', 'War of the Arrows', 'Red Cliff II', 'The Yellow Sea', 'Pusher', 'Along with the Gods: The Two Worlds', 'The Baader Meinhof Complex', 'Berserk: The Golden Age Arc I - The Egg of the King', 'Vampire Hunter D: Bloodlust', 'La Femme Nikita', 'Black Dynamite', 'Evangelion: 1.0 You Are (Not) Alone', 'The Assassination of Jesse James by the Coward Robert Ford', 'The Raid 2', 'Tombstone', 'Lethal Weapon 2', "The World's End", 'American Sniper', 'The Nice Guys', "Guy Ritchie's The Covenant", 'The Trip', 'Minnal Murali', 'Blood Diamond', 'The Misfits', '21 Jump Street', '48 Hrs.', 'Beverly Hills Cop', 'In China They Eat Dogs', 'The Outpost', 'Narvik', 'Wrath of Man', 'The Northman', "The Wolf's Call", 'Deadpool 2', 'Game Night', 'A Prayer Before Dawn', 'The Night Comes for Us', 'Hotel Mumbai', 'The Navigator', 'Destry Rides Again', 'The Sword of Doom', 'Ride the High Country', "Twelve O'Clock High", 'Black Friday', 'El Infierno', 'Andaz Apna Apna', 'Flame & Citron', 'Always', 'Shogun Assassin', 'Miracle Mile', 'North Face', 'Fanaa', 'Airlift', 'The Admiral: Roaring Currents', 'Police Story 3: Super Cop', 'Ink', 'Set It Off', 'Casualties of War', 'Juice', 'Fist of Fury', 'The Good, the Bad, the Weird', 'Ong Bak: Muay Thai Warrior', 'Grosse Pointe Blank', 'Flags of Our Fathers', 'The Warriors', 'Escape from New York', 'The Last Samurai', 'Predator', 'Spy', 'Mosul', 'Rumble Fish', 'Undisputed III: Redemption', 'Stripes', 'Lust, Caution', 'Ready or Not', 'The Gentlemen', 'The Enemy Below', 'Delhi Belly', 'State of Grace', 'Point Blank', 'Neon Genesis Evangelion: Death and Rebirth', 'The Connection', 'Vanishing Point', 'Mongol: The Rise of Genghis Khan', 'They Call Me Jeeg', 'Ichi the Killer', 'El Mariachi', 'A Most Violent Year', 'The Negotiator', 'They Live', 'Attack the Block', 'Point Break', 'Natural Born Killers', 'Falling Down', 'Apocalypto', 'The Rock', 'Tropic Thunder', 'Patriots Day', 'Watchmen', 'The Big Easy', 'Dog Soldiers', 'Batman & Mr. Freeze: SubZero', 'Courage Under Fire', 'The Sea Hawk', 'Brother 2', 'Mad Max', 'Hamburger Hill', 'The Matrix Reloaded', 'The Great Race', 'Memoir of a Murderer', 'Blade of the Immortal', 'The Old Guard', 'Suicide Squad: Hell to Pay', 'High Sierra', 'Run Silent, Run Deep', 'El Cid', 'The Professional', 'Persuasion', 'SPL: Kill Zone', 'Cross of Iron', 'New World', 'OSS 117: Cairo, Nest of Spies', 'District B13', "Dragon Ball Z: Resurrection 'F'", 'Bronson', 'We Were Soldiers', 'The Guest', 'Justice League Dark', 'Ronin', 'The Raid', 'Enemy of the State', '22 Jump Street', 'Athena', 'Shershaah', 'Chocolate', 'Planet Terror', 'Sands of Iwo Jima', 'Violent Cop', 'New Jack City', 'T-34', 'Until the End of the World', 'The Gangster, the Cop, the Devil', 'Avengement', 'The Mark of Zorro', "Von Ryan's Express", 'Anniyan', 'Last Life in the Universe', 'Eega', 'A Better Tomorrow II', 'Tai-Chi Master', 'Wheels on Meals', 'Southern Comfort', 'Max Manus: Man of War', 'Once Upon a Time in China', 'Easy Money', 'Thunderbolt and Lightfoot', 'Vampire Hunter D', 'The Day After', 'Free to Play', 'Bound by Honor', 'Stewie Griffin: The Untold Story', 'In Order of Disappearance', 'The Way of the Dragon', 'THX 1138', 'Resident Evil: Damnation', 'The Girl Who Played with Fire', 'Dawn of the Dead', 'True Lies', 'Die Hard 2', 'Die Hard: With a Vengeance', 'Fury', 'Kingsman: The Secret Service', 'The Last Kingdom: Seven Kings Must Die', 'Flickering Lights', 'Taxi', 'The Most Dangerous Game', 'Alexander Nevsky', 'The Driver', 'Faster, Pussycat! Kill! Kill!', 'The Stunt Man', 'The Patriot', 'Vada Chennai', 'Ala Vaikunthapurramuloo', 'Little Caesar', 'Vishwaroopam', 'Paan Singh Tomar', 'Let the Bullets Fly', 'A Chinese Ghost Story', 'Shoot to Kill', 'Dragon', 'Bajirao Mastani', 'Sultan', 'Jin-Roh: The Wolf Brigade', 'Armour of God', 'Rob Roy', 'Undisputed II: Last Man Standing', 'Magnum Force', 'Joy Ride', 'Gantz:O', 'Sympathy for Mr. Vengeance', 'The Score', 'eXistenZ', 'The Siege of Jadotville', 'Elite Squad', 'Pineapple Express', 'The Girl with All the Gifts', 'Lone Survivor', 'Allied', 'Dredd', 'This Is the End', 'Prison Break: The Final Break', 'Rocketry: The Nambi Effect', 'Ferry', 'Brotherhood of the Wolf', 'Colors', 'Death Proof', 'Law of Tehran', 'Danger Close: The Battle of Long Tan', 'The Art of Self-Defense', 'Bad Boys for Life', 'Dragged Across Concrete', 'Jigarthanda', 'Kaminey', 'Ashes of Time', 'Badlapur', 'The Mountain II', '13 Tzameti', 'Koi... Mil Gaya', 'The Inglorious Bastards', 'Baby', 'Shaft', 'Little Big Soldier', 'The Big Boss', 'JCVD', 'Rumble in the Bronx', 'Felon', 'Jackass Number Two', 'The Wave', 'The Life Aquatic with Steve Zissou', 'The Grey', 'Enemy at the Gates', 'Southpaw', 'American Made', 'The Equalizer', 'Malik', 'Plane', 'Space Sweepers', 'The Stronghold', 'Marco Polo: One Hundred Eyes', '28 Weeks Later', 'The Lizard', 'Unleashed', 'Curse of the Golden Flower', 'Spartan', 'Get the Gringo', 'Boss Level', 'Major Grom: Plague Doctor', '#Alive', 'Batman: Gotham by Gaslight', 'Birds of Prey (and the Fantabulous Emancipation of One Harley Quinn)', 'Mayhem', 'Atomic Blonde', 'The Vikings', 'The Good Thief', '24', "Bang Bang You're Dead", 'Gangster No. 1', 'French Connection II', 'Fifty Dead Men Walking', 'Outrage', 'Fan', 'The Thieves', 'Avalon', 'Paid in Full', 'The Matador', 'Micmacs', 'Witching & Bitching', 'Romper Stomper', 'OSS 117: Lost in Rio', 'Blood and Bone', 'The Edge', 'Heartbreak Ridge', 'Slow West', 'Turbo Kid', 'Harry Brown', 'Patriot Games', 'From Dusk Till Dawn', 'Blood Father', 'Ambulance', 'Copshop', 'Satya', 'Con Air', 'Coffy', 'Wanted', 'Death Wish', 'Master', 'Tanhaji: The Unsung Warrior', 'Sonchiriya', 'Vaaranam Aayiram', 'Thuppakki', 'Intacto', 'The Emerald Forest', 'The Long Riders', 'Heaven & Earth', 'Thursday', 'New Police Story', 'The Villainess', 'Deathgasm', 'Stretch', 'The Salvation', 'Boyka: Undisputed IV', "The Girl Who Kicked the Hornet's Nest", 'Spy Game', 'RocknRolla', 'Kingdom of Heaven', 'Overlord', 'Man on Fire', 'Blade', 'Kick-Ass', '300', 'Violent Night', 'Lakshya', 'Arlington Road', 'Cop Land', 'Robin-B-Hood', 'Starship Troopers', 'Bullet Train', 'Major', 'Theeran Adhigaaram Ondru', 'Accident Man', 'Crawl', 'Anthropoid', 'Vikram Vedha', 'Raid', 'War', "Black '47", '21 Bridges', 'Hatari!', 'The Breath', 'Detective Byomkesh Bakshy!', 'Confession of Murder', 'Juan of the Dead', 'Admiral', 'Dead Presidents', 'Shaolin', 'The Protector', 'Three Steps Above Heaven', 'The Legend Is Born: Ip Man', 'Backdraft', 'Ransom', 'Jackass 3D', 'Under Siege', "Shoot 'Em Up", 'Conan the Barbarian', 'Desperado', 'Air Force One', 'Blade II', 'The Heat', 'Sita Ramam', 'Bad Taste', 'Dobermann', 'Death Race 2000', 'Lucifer', 'Extraction', 'Black and Blue', 'The Angel', 'Zombieland: Double Tap', 'Maqbool', 'Golmaal - Fun Unlimited', 'Agneepath', 'Versus', 'Infernal Affairs III', '9th Company', 'Into the White', 'Dead Snow 2: Red vs. Dead', 'We Own the Night', 'Wheelman', 'The Last Castle', 'Taxi 2', 'Payback', 'Defiance', 'Four Brothers', 'Commando', 'Team America: World Police', 'Crank', 'The Boondock Saints', 'Shooter', '2 Guns', 'Equilibrium', 'Once Upon a Time in Mexico', 'Kiss of the Dragon', 'Aśoka', 'Troy', 'The Hitcher', "The Devil's Double", 'The Kingdom', 'Doodlebug', 'Kaabil', 'Bharat Ane Nenu', 'Sicario: Day of the Soldado', 'Darr', 'Arjun Reddy', 'Sarfarosh', 'Waterloo', 'Welcome', 'Shinjuku Incident', 'Don 2', 'Raees', 'Zulu', 'Kill the Irishman', 'Running Scared', 'The Long Kiss Goodnight', 'Fallen', 'The Last Boy Scout', 'God Bless America', 'Highlander', 'Body of Lies', 'Machete', 'Pitch Black', 'The Accountant', 'Rollerball', 'Dhamaal', 'Singham', 'The Brave One', "Cheech & Chong's Next Movie", 'Those Who Wish Me Dead', 'Terminator: Dark Fate', 'Outlaw King', 'The Informer', 'Athadu', 'Baasha', '1: Nenokkadine', 'Deewaar', 'Madras Cafe', 'The Program', 'The Ghazi Attack', 'Subway', 'The Business', 'Crying Freeman', 'Blackthorn', 'The Dark Valley', 'Forsaken', 'The Book of Eli', 'An Action Hero', 'Army of Thieves', 'Day Shift', 'The Punisher: Dirty Laundry', 'Day Watch', 'The Expendables 2', 'Lethal Weapon 3', 'Khakee', 'What Happened to Monday', 'Petta', 'Parmanu: The Story of Pokhran', 'Kesari', 'Pokiri', 'Roja', 'Indian', 'Ayan', 'Kaththi', 'Mr. India', 'The Wild Geese', 'Class of 1984', 'Azumi', 'Confidence', 'The Toxic Avenger', 'Conspiracy Theory', 'The Running Man', 'Demolition Man', 'Free State of Jones', 'Law Abiding Citizen', 'Bad Boys', 'The Protégé', 'AK vs AK', 'Safe House', 'Night Watch', 'The Foreigner', 'Code 8', 'Ratsasan', 'Den of Thieves', 'Kingsman: The Golden Circle', 'Mankatha', 'Theri', 'Kaho Naa... Pyaar Hai', 'The Escapist', 'The Legend of Billie Jean', 'City Hunter', 'The Hunting Party', 'The Way of the Gun', 'The Great Raid', 'Son of a Gun', 'Jackass: The Movie', 'Filth', '13 Hours: The Secret Soldiers of Benghazi', "The Hitman's Bodyguard", 'Big Nothing', 'Bloodsport', 'Exodus', 'Shinobi: Heart Under Blade', 'The Matrix Revolutions', 'Constantine', "Don't Breathe 2", 'Mersal', '12 Strong', 'Ghajini', 'Company', 'Don', 'Irudhi Suttru', 'Oye Lucky! Lucky Oye!', 'Sarkar', 'Mardaani', 'Merantau', 'Aqua Teen Hunger Force Colon Movie Film for Theaters', 'Tales from the Crypt: Demon Knight', 'Rambo', 'Olympus Has Fallen', 'Operation Fortune: Ruse de Guerre', 'The Bodyguard', 'Time Trap', 'Holiday', 'Foxy Brown', 'To End All Wars']

# from tmdb import is_movie_or_tv_show

# checked_titles = []
# titles = ['North by Northwest', 'Evangelion: 3.0+1.0 Thrice Upon a Time', 'Oldboy', 'Aliens', 'Mad Max: Fury Road']

# for title in titles:
#     # print("Chec#king title: {}".format(title))
#     res = is_movie_or_tv_show(title, api_url="https://api.themoviedb.org/3",
#                               api_key="cea9c08287d26a002386e865744fafc8")
#     if res == "tv" or res == "show":
#         print("Title: {} is a tv show".format(title))
#         titles.remove(title)
#     elif res == "movie":
#         print("Title: {} is a movie".format(title))
#         checked_titles.append(title)
#     else:
#         print("Title: {} is not found".format(title))

# print("All done!")
# print("Checked titles: {}".format(checked_titles))

from orionoid import search_best_qualities

ids = {'North by Northwest': 'tt0053125', 'Evangelion: 3.0+1.0 Thrice Upon a Time': 'tt2458948', 'Oldboy': 'tt1321511', 'Aliens': 'tt0090605', 'Mad Max: Fury Road': 'tt1392190', 'Demon Slayer -Kimetsu no Yaiba- The Movie: Mugen Train': 'tt11032374', 'Neon Genesis Evangelion: The End of Evangelion': 'tt0169858', 'The French Connection': 'tt0067116', 'Children of Men': 'tt0206634', 'RRR': 'tt8178634', 'Everything Everywhere All at Once': 'tt6710474', 'Heat': 'tt0113277', 'Kill Bill: Vol. 2': 'tt0378194', 'Riders of Justice': 'tt11655202', 'Scarface': 'tt0086250', 'Logan': 'tt3315342', 'Bacurau': 'tt2762506', 'The Killer': 'tt1136617', 'Blade Runner': 'tt0083658', 'Justice League Dark: Apokolips War': 'tt11079148', 'A Bittersweet Life': 'tt0456912', 'A Night to Remember': 'tt0051994', 'Sin Nombre': 'tt1127715', 'Akira': 'tt0094625', 'Ghost in the Shell': 'tt0113568', 'Blade Runner 2049': 'tt1856101', 'Baby Driver': 'tt3890160', 'Drive': 'tt0780504', '1917': 'tt8579674', 'John Wick: Chapter 3 - Parabellum': 'tt6146586', 'Fallen Angels': 'tt0112913', 'Train to Busan': 'tt5700672', 'Pusher II': 'tt0396184', 'Speed': 'tt0111257', 'Braveheart': 'tt0112573', 'Die Hard': 'tt0095016', 'John Wick: Chapter 2': 'tt4425200', "Mortal Kombat Legends: Scorpion's Revenge": 'tt9580138', 'Assault on Precinct 13': 'tt0398712', 'Bāhubali: The Beginning': 'tt2631186', 'Headhunters': 'tt1614989', 'End of Watch': 'tt1855199', 'Sicario': 'tt3397884', 'The Revenant': 'tt1663202', 'Soorarai Pottru': 'tt10189514', 'Batman: The Long Halloween, Part Two': 'tt14402926', 'The Harder They Fall': 'tt10696784', 'Lock, Stock and Two Smoking Barrels': 'tt0120735', 'True Romance': 'tt0108399', 'Collateral': 'tt0369339', 'Léon: The Professional': 'tt0110413', 'Jackass Forever': 'tt11466222', 'A Taxi Driver': 'tt6878038', 'The Guns of Navarone': 'tt0054953', 'The Age of Shadows': 'tt4914580', 'The Last of the Mohicans': 'tt0104691', 'Ip Man': 'tt21028848', 'Old Henry': 'tt12731980', 'Prey': 'tt11866324', 'All Quiet on the Western Front': 'tt1016150', 'RoboCop': 'tt0093870', 'Ip Man 2': 'tt1386932', 'Nobody': 'tt7888964', 'The Witcher: Nightmare of the Wolf': 'tt11657662', 'El Camino: A Breaking Bad Movie': 'tt9243946', 'May God Save Us': 'tt4944596', 'Evangelion: 2.0 You Can (Not) Advance': 'tt0860906', 'In the Line of Fire': 'tt0107206', "'71": 'tt2614684', 'Crimson Tide': 'tt0112740', 'Kung Fury': 'tt3472226', 'Gladiator': 'tt0172495', "Zack Snyder's Justice League": 'tt12361974', 'The Blues Brothers': 'tt0080455', 'The Suicide Squad': 'tt6334354', 'Upgrade': 'tt6499752', 'Rurouni Kenshin Part III: The Legend Ends': 'tt3029556', 'Cowboy Bebop: The Movie': 'tt0275277', 'Layer Cake': 'tt0375912', 'Face/Off': 'tt0119094', 'Eye in the Sky': 'tt2057392', 'Total Recall': 'tt1386703', 'John Wick': 'tt2911666', 'The Last Duel': 'tt4244994', 'The Unbearable Weight of Massive Talent': 'tt11291274', 'Udta Punjab': 'tt4434004', 'Deadpool': 'tt1431045', 'Uri: The Surgical Strike': 'tt8291224', 'Pusher 3': 'tt0425379', '36th Precinct': 'tt0390808', 'Infernal Affairs II': 'tt0369060', 'Pusher': 'tt0117407', 'Tombstone': 'tt0108358', 'American Sniper': 'tt2179136', 'The Nice Guys': 'tt3799694', "Guy Ritchie's The Covenant": 'tt4873118', 'The Misfits': 'tt4876134', 'Beverly Hills Cop': 'tt0086960', 'Wrath of Man': 'tt11083552', 'The Northman': 'tt11138512', "The Wolf's Call": 'tt7458762', 'Deadpool 2': 'tt5463162', 'Game Night': 'tt2704998', 'The Night Comes for Us': 'tt6116856', 'Hotel Mumbai': 'tt5461944', 'Black Friday': 'tt11649338', 'El Infierno': 'tt1692190', 'The Admiral: Roaring Currents': 'tt3541262', 'Grosse Pointe Blank': 'tt0119229', 'The Last Samurai': 'tt0325710', 'Predator': 'tt0093773', 'Spy': 'tt3079380', 'Mosul': 'tt8354112', 'Ready or Not': 'tt7798634', 'The Gentlemen': 'tt8367814', 'Delhi Belly': 'tt1934231', 'Point Blank': 'tt2499472', 'The Connection': 'tt9826820', 'A Most Violent Year': 'tt2937898', 'The Negotiator': 'tt0120768', 'Falling Down': 'tt0106856', 'The Rock': 'tt0117500', 'Tropic Thunder': 'tt0942385', 'Patriots Day': 'tt4572514', 'Watchmen': 'tt0409459', 'Batman & Mr. Freeze: SubZero': 'tt1877830', 'Courage Under Fire': 'tt0115956', 'Mad Max': 'tt0079501', 'Memoir of a Murderer': 'tt5729348', 'Suicide Squad: Hell to Pay': 'tt7167602', 'OSS 117: Cairo, Nest of Spies': 'tt0464913', 'Bronson': 'tt1172570', 'We Were Soldiers': 'tt0277434', 'The Guest': 'tt2980592', 'Justice League Dark': 'tt2494376', 'Enemy of the State': 'tt0120660', 'Athena': 'tt15445056', 'Shershaah': 'tt10295212', 'Planet Terror': 'tt1077258', 'T-34': 'tt8820590', 'The Gangster, the Cop, the Devil': 'tt10208198', 'Avengement': 'tt8836988', 'Free to Play': 'tt3203290', 'Stewie Griffin: The Untold Story': 'tt0385690', 'Resident Evil: Damnation': 'tt1753496', 'Die Hard: With a Vengeance': 'tt0112864', 'Fury': 'tt2713180', 'Kingsman: The Secret Service': 'tt2802144', 'The Last Kingdom: Seven Kings Must Die': 'tt15767808', 'The Driver': 'tt0077474', 'The Patriot': 'tt0187393', 'Gantz:O': 'tt5923962', 'The Siege of Jadotville': 'tt3922798', 'Elite Squad': 'tt0861739', 'Pineapple Express': 'tt0910936', 'The Girl with All the Gifts': 'tt4547056', 'Allied': 'tt3640424', 'This Is the End': 'tt1245492', 'Rocketry: The Nambi Effect': 'tt9263550', 'Ferry': 'tt14217100', 'Law of Tehran': 'tt9817070', 'Danger Close: The Battle of Long Tan': 'tt0441881', 'The Art of Self-Defense': 'tt7339248', 'Bad Boys for Life': 'tt1502397', 'Dragged Across Concrete': 'tt6491178', 'The Inglorious Bastards': 'tt0076584', 'The Life Aquatic with Steve Zissou': 'tt0362270', 'The Grey': 'tt1601913', 'Enemy at the Gates': 'tt0215750', 'American Made': 'tt3532216', 'The Equalizer': 'tt0455944', 'Malik': 'tt7696274', 'Plane': 'tt5884796', 'Space Sweepers': 'tt12838766', 'The Stronghold': 'tt10404944', '28 Weeks Later': 'tt0463854', 'Unleashed': 'tt0342258', 'Boss Level': 'tt7638348', 'Major Grom: Plague Doctor': 'tt7601480', 'Batman: Gotham by Gaslight': 'tt7167630', 'Birds of Prey (and the Fantabulous Emancipation of One Harley Quinn)': 'tt7713068', 'Mayhem': 'tt4348012', 'Atomic Blonde': 'tt2406566', 'Avalon': 'tt0267287', 'Witching & Bitching': 'tt2404738', 'OSS 117: Lost in Rio': 'tt1167660', 'The Edge': 'tt0119051', 'Slow West': 'tt3205376', 'Turbo Kid': 'tt3672742', 'From Dusk Till Dawn': 'tt0116367', 'Ambulance': 'tt4998632', 'Copshop': 'tt5748448', 'Con Air': 'tt0118880', 'Wanted': 'tt0493464', 'Death Wish': 'tt1137450', 'Stretch': 'tt2494280', 'The Salvation': 'tt2720680', 'Boyka: Undisputed IV': 'tt3344680', 'RocknRolla': 'tt1032755', 'Overlord': 'tt4530422', 'Man on Fire': 'tt0328107', 'Blade': 'tt0120611', 'Kick-Ass': 'tt1250777', '300': 'tt0416449', 'Violent Night': 'tt12003946', 'Starship Troopers': 'tt0120201', 'Bullet Train': 'tt12593682', 'Accident Man': 'tt6237612', 'Crawl': 'tt8364368', 'Anthropoid': 'tt4190530', "Black '47": 'tt3208026', '21 Bridges': 'tt8688634', 'Admiral': 'tt2544766', 'Backdraft': 'tt0101393', "Shoot 'Em Up": 'tt0465602', 'Air Force One': 'tt0118571', 'Blade II': 'tt0187738', 'The Heat': 'tt2404463', 'Sita Ramam': 'tt20850406', 'Black and Blue': 'tt7390646', 'The Angel': 'tt5968274', 'Zombieland: Double Tap': 'tt1560220', 'Dead Snow 2: Red vs. Dead': 'tt2832470', 'We Own the Night': 'tt0498399', 'Wheelman': 'tt5723286', 'The Last Castle': 'tt0272020', 'Crank': 'tt0479884', 'The Kingdom': 'tt15767808', 'Sicario: Day of the Soldado': 'tt5052474', 'Fallen': 'tt0775362', 'Highlander': 'tt0091203', 'Those Who Wish Me Dead': 'tt3215824', 'Terminator: Dark Fate': 'tt6450804', 'Outlaw King': 'tt6679794', 'The Informer': 'tt1833116', 'The Program': 'tt3083008', 'Blackthorn': 'tt1629705', 'Forsaken': 'tt2271563', 'An Action Hero': 'tt15600222', 'Army of Thieves': 'tt13024674', 'Day Shift': 'tt13314558', 'The Punisher: Dirty Laundry': 'tt2280378', 'The Expendables 2': 'tt1764651', 'Confidence': 'tt0310910', 'The Protégé': 'tt6079772', 'AK vs AK': 'tt11651796', 'Safe House': 'tt1599348', 'The Foreigner': 'tt1615160', 'Code 8': 'tt6259380', 'Den of Thieves': 'tt1259528', 'Kingsman: The Golden Circle': 'tt4649466', 'The Great Raid': 'tt0326905', 'Jackass: The Movie': 'tt0322802', 'Filth': 'tt1450321', '13 Hours: The Secret Soldiers of Benghazi': 'tt4172430', "The Hitman's Bodyguard": 'tt1959563', 'Constantine': 'tt0360486', "Don't Breathe 2": 'tt6246322', '12 Strong': 'tt1413492', 'Aqua Teen Hunger Force Colon Movie Film for Theaters': 'tt0455326', 'Olympus Has Fallen': 'tt2302755', 'Operation Fortune: Ruse de Guerre': 'tt7985704', 'Time Trap': 'tt4815122', 'Holiday': 'tt0030241'}

QUALITIES_SETS = [["hd1080", "hd720"], ["hd4k"]]
FILENAME_PREFIX = "result"
for title, imdb_id in ids.items():
    print("Searching for title: {}".format(title))
    search_best_qualities(title=imdb_id, title_type="movie", qualities_sets=QUALITIES_SETS, filename_prefix=FILENAME_PREFIX)
    print("Done for title: {}".format(title))

print("All done!")
