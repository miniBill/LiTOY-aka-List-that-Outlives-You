# LiTOY : the List That Outlives You.

Table of contents
=================
* [Current state](#Current_state)
* [What is LiTOY?](#What_is_LiTOY?)
* [FAQ](#FAQ)
* [How can I use LiTOY?](#How_can_I_use_LiTOY?)
    * [Syntax and usage example](#Syntax_and_usage_example)
* [TODO](#TODO)
* [Acknowledgement](#Acknowledgement_(not_ordered))

Current state
===============
* personal project
* beta stage
* PRs and issues are extremely appreciated.
* **PEP8 compliant**
* All functions include docstrings
* Type hinting the code is planned but not yet done

What is LiTOY?
==============
There are several ways to look at it :
* LiTOY is a python script using pandas to create and manage a list of your goals. Those goals or objectives can be short, medium or long term. The idea is to rank them in a smart way using pairwise comparisons and several [ELO scores](https://en.wikipedia.org/wiki/Elo_rating_system).
* A way to always follow the gradient of optimally-spent time : using LiTOY you always do what's most important and quick to do.
* An organizer aiming at centralizing all your goals in a single place while quickly ranking them in an order reflecting user preferences.
* A way for me to increase my Python skills.
* A way to get better at creating [Eisenhower Matrices](https://productiveclub.com/eisenhower-matrix/).


The idea behind LiTOY is simple : 
1. note all your goals in a text file (one task by line)
2. have LiTOY import this file into a DataFrame and fetch all relevant metadata (example : length of time to watch a youtube video you linked)
3. let LiTOY pick items and prompt the user for which is better (according to a user-specified question)
4. answer the question to adjust the ELO score of each item accordingly
5. When enough pairwise comparisons are done, the items will be ranked. You can then know at a glance what's important to do but at the same time quick to finish.


FAQ
===
**Where does the idea come from?** From Gwern's [media resorted](https://www.gwern.net/Resorter).

**Do you have any idea it will work or at least converge towards something useful without doing thousands of comparisons a day?** Not really, but quick back-of-the-envelope calculation made it look doable.

**What does LiTOY stand for?** It stands for `List that Outlives You`. It is used as a [memento mori](https://en.wikipedia.org/wiki/Memento_mori)

**Do you accept criticism and/or contribution?** All help and criticisms are very appreciated.

**What are ELO scores? Why did you choose this algorithm?** A ranking system initially devised for chess. The idea is that if you have chess players A, B and C : if `A beats B` and `B beats C` then you don't really have to organize a fight between A and C to know which is better. It does so by assigning a score to each opponent that can then be used to compare opponents that have never met each other. The main selling point of ELO is that it still behaves well even if some players occasionally under perform (or over perform). In the case of LiTOY, you can have some incoherent comparisons in your database and it will not throw off the whole ranking. Also, ELO is dead easy to implement and I wanted to completely understand (i.e. grok) my code.

**What platform does it run on?** I tried to make it as agnostic as possible but I'm on Linux and hate other systems. Normally the code should run fine on other systems but please do tell me if you run into an issue.

**Why store the file as an excel file?** Because if you run libreoffice you can quickly have a gui to edit the database, whereas handling sqlite or other formats is not as user friendly. There is an option to save the database in json regularly to avoid data loss though.

**How can I undo X?** It is not really possible for now. But you can access the logs and see what you did wrong. Hopefully this can help you repair damage. Rollback features might be added sometime in the future. If you have any issue feel free to open one, especially if you think your action was not recorded in the log.

**What are answer level number ?** If you answer 1 it means you favor the entry on the left compared to the one on the right. 4 means you favor the right one. 3 is obviously the middle ground but is not the same as skipping the fight. Of course, all this is relative to the question that is being considered.

**Any killer features you want to brag about?** LiTOY automatically retrieves lots of metadata from the links. Like reading time from a pdf, a webpage, duration of a video etc. Also, it's mostly in one single file, making it somewhat easier to understand how it works and to maintain.

**Is there a way to ask litoy to fetch metadata for a video that is not on youtube?** Yes, just add somewhere `type:video` in the entry. you can also use `type:local_video` for local files using `ffmpeg`. Don't hesitate to use quotation marks (`"`) to avoid running into issues with unix spaces in links.

**Do you care to explain all the different fields in the database?** 
* `ID` used for the pandas index as well as the line number in excel. This should in theory never change for a given entry (even if you edit the content of the entry).
* `date` date in unix time in second of the creation of this entry
* `content` the text content of the entry
* `metacontent` all relevant metadata that LiTOY extracted from `content`, for example url, video duration, time to read a pdf, etc
* `tags` user-specified tags of the entry. You can specify them during comparison or when adding the entry (syntax : `my task is to do X tags:something tags:something else`)
* `starred` used to differentiate this entry from the rest
* `iELO`, `tELO` importance ELO score and time ELO score. A high `iELO` means that the task is important. A high `tELO` means that the task is quick to do.
* `DiELO`, `DtELO` D stands for Delta, as in the difference between two quantities. The `DiELO` value of an entry is the difference between its current and previous `iELO`. This is used to know which entry moved the most in its most recent comparisons. This information is relevant to approach optimality when picking entries for comparisons.
* `gELO` g stands for Global. The global score merges `iELO` and `tELO` in a common metric. This way the user just has to display the `podium` to prioritise tasks.
* `K` the K factor of an entry is a value that starts high and gradually decreases. It decreases after each comparison. It appears when calculating ELO scores as a multiplicating factor. It is common in chess tournament etc. The idea is that a new entry has a bonus that makes each win or loss more impactful on its ranking to help it find its true rank faster.  Entries that have already been compared many times will have more inertia.
* `compar_time` simply the amount of time spent comparing this entry
* `n_comparison` simply the number of times this entry has been compared
* `disabled` is 1 if the user decided to disable this entry. It will not appear in the podium or during comparisons but will remain in the database. You can use this if you have accomplished the task or if you decide that you won't ever do it.

**What is the podium?** just a way to show the entries with the highest global scores

**What does it mean to answer 1 vs 2345 ?** 1 means you favor the one on the left, strongly. 5 means you favor the one on the right strongly. 3 means they are equal, 2 and 4 are intermediate score ("I prefer left over right, but not that strongly"). Remember that this will change ELOs for *both* cards at every fight.

**Where can I see the correct syntax to use when writing a file destined for importation?** See [this file](./example_new_entry.txt)

**What is the difference between the entry on the left and on the right?** LiTOY actually picks 11 entries : one is the reference entry on the left and all the others appear on the right. This way it is way easier for the mind to compare in a row.

**Can I open the database using libreoffice?** Yes, it's why I chose this format. But close LiTOY first and don't forget to save your changes. Note that you can automatically save the whole database as a json file too.

How can I use LiTOY?
====================
* Read this page thoroughly. Don't be afraid to ask questions.
* make sure you have python 3.9 installed
* `git clone https://github.com/thiswillbeyourgithub/LiTOY/ && cd LiTOY`
* manually edit the settings at the top of `LiTOY.py`
* run `pip3.9 install -r requirements.txt`
* `python3.9 ./LiTOY.py --help`
*I recommend setting an alias in your shell, mine is `alias litoy = 'cd /litoy/folder && python3.9 ./LiTOY.py -l personnal_database.xlsx'` then I just have to type `litoy -r`

Syntax and usage example:
-------------------------

`python3.9 LiTOY.py --litoy-db database.xlsx --add 'repair the tires tags:diy'
   * adds a new entry to deck todo with the tag diy 

`python3.9 LiTOY.py --litoy-db database.xlsx --review
   * automatically pick 10 cards and compare them (20 comparison to do because you have 2 questions each time, this can be changed in the settings)

`python3.9 LiTOY.py --litoy-db database.xlsx --import-from-file file.txt`
    * Automatically imports from the file. Each line becomes an entry. Except if it is already part of the database. Lines beginning with `#` are ignored. Metadata will be automatically retrieved so be patient.
    * To see example of the syntax for the import file, read [this file](./example_new_entry.txt)


TODO
======
    * implement a two letter shortcut code to answer importance and time at the same time?
    * use type hints from the beginning and mypy
    * use side by side function to display the podium
    * open libreoffice with an argument
    * add gif to show demo
    * answer to this guy https://www.lesswrong.com/posts/54Bw7Yxouzdg5KxsF/how-do-you-organise-your-reading
    * when stable: talk about it on psionica, then lesswrong



Acknowledgement (not ordered)
=============================
* Thanks to Emile Emery for his help in determining the best sorting algorithm to use and implementing it.
* Thanks to [Kryzar (Antoine Leudière)](https://github.com/kryzar) for his insight on UI.
