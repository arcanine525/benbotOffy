# Interacting with Ben Bot:
* All commands to the Ben bot must be prefixed by `/ben <command>`, e.g. `/ben help`. You can also use `ben <command>` (without `/`)
* You can use alternative Ben's alias like `/dinh`. To see more Ben's alias use `/ben alias`.
# Some basic command:

`/ben alias`
* To see more Ben's alias. 
* Sample output: `bot alias: /bot, /dinh, ben, /ben, dinh, /vic`

`/ben chat <your-message>`
* Chat with Ben. 
* Example:
    * Input: `/ben chat hello`
    * Output: `Cleverbot is silent` (It's may be some bugs here)

`/ben dinh_refresh`
* Refresh [Dinh](https://dinh.officience.com/) database
* Sample output: `Refresh, proceeding...
                    Refresh completed`

`/ben dnd`
* Toggle `do not disturb` mode.
* It will last for 6 hours by default.
* You can modify how long it will last by add number (in hour) after this command
* Example: 
    * Input: `/ben dnd 2`
    * Output: `global DND toggled ON for Hoang Hiep Le, expires in 2.0 hour(s)`

`/ben harper`
* To see random quote.
* Example: 
`"They say time will make all this go away. But it's time that's taken my tomorrow, and turned them into yesterday."
– Ben Harper `

`/ben help`
* See available commands.
* You can see available argument for specific command by using: `/ben help <command-name>`. 
* Sample output: 
`User commands:
bemorespecific, botalias, chat, computetopinfluencer, dinh_refresh, dnd, echo, harper, help, iamspartacus, kenobi, noinfluencer, nosalary, offycauses, offypr, opportunity, optout, ping, project, pushbulletapi, remindall, remindme, room, setnickname, sos, statistics, timesheet, topinfluencer, topproximityinfluencer, topsalary, topspiritualinfluencer, verifyme, version, whoami, whois`

`/ben noinfluencer`
* See all Offies do not have any influencers at the moment.
* Sample output: 
`72 Offies do not have any influencers for the moment :  ... `

`/ben nosalary`
* See all Offies have not set their salaries at the moment.
* Sample output: `72 Offies have not set their salaries for the moment : ...`

`/ben offycauses`
* See a video clip about Offy causes. (Please subscribe channel if you like it).

`/ben offypr`
* Get infomation about PR process

`/ben opportunity <status> <name>`
* Get information about opportunities related to a status and/or a company name.
* Sample input: `ben opportunity qualification ekino`

`/ben optout`
* Toggles opt-in/opt-out of advanced bot features.
* Sample output: `Hoang Hiep Le, you opted-out from bot private messages`

`/ben ping`
* Bot replies with a `pong`

`/ben project <project_name>`
* Get information about a project.
* Example:
    * Input: 
    * Output: 
    `Aperoffy VN
            Parent Analytic Account : Engagement
            Team : Hubert Delorme, Khac Khanh NGO, Minh Ngoc HUYNH, Khac Phu NGUYEN, Claire Mériel, Emmanuelle Durand, Dieu Uyen DANG, 
            Total time spent : 161.25 hours
            During the week of the 2018-10-08, 0 hours spent`

`/ben remindall <time> <message>`
* Send the remind message to the chat after a delay time (in minute).
* Example: 
    * Input: `/ben remindall 1 hi all` 
    * Output: `Public reminder in 1m` after 1 minute you will receive a message `Reminder: hi all` 

`/ben remindme <time> <message>`
* Send the remind message to you after a delay time (in minute).
* Example: 
    * Input: `/ben remindme 1 hello` 
    * Output: `Private reminder for Hoang Hiep Le in 1m` after 1 minute you will receive a message `Reminder: hello` 

`/ben setnickname <nick_name>`
* Set nickname for you.
* You can check it by using `/ben whoami`
* Exmaple: 
    * Input: `/ben setnickname arcanine`
    * Output: `Setting nickname to 'arcanine'`

`/ben statistics`
* Show how many times each command was used.
* Sample output: 
 `2018-10-16 : room : 26, sos : 69, opportunity : 120, whois : 845, refresh : 6, project : 45, timesheet : 70, project : 46`

`/ben timesheet <name_of_offy>`
* Get information about Offies activities. Without argument you will have information for all the company.
* Example: 
    * Input: `ben timesheet`
    * Output: 
    `On the week of the 2018-10-08, 33 % of the timesheets have been completed (1)
The tribe's mood is 5/10`

`/ben topinfluencer`
* List top member have more than 10 followers.
* Sample ouput: 
`Top influencers with more than 10 followers: 
Thao Lan NGUYEN HOANG (32) 
Cao Phong DUONG (27) 
Duc HA DUONG (23) ...`

`/ben topsalary`
* List top offies salary.
* Sample output: `17 Offies earn more than 22M VND: ...`

`/ben topspiritualinfluencer`
* List top spiritual influencers.
* Sample output: `Top spiritual influencers with more than 5 followers: ...`

`/ben verifyme`
* Verify that the you has a 1-to-1 conversation with the bot.
* Sample output: `verification completed - this is your one-to-one chat with the bot`

`/ben version`
* Check Ben version 
* Sample output: `Bot Version: 2.7.10`

`/ben whois <offy_name>`
* Get infomation about offy member.
* Example: 
    * Input: `/ben whois Hoang Hiep`
    * Output: 
     `Hoang Hiep Le
        Cluster : IT Crew / Intern`

`/ben horoscope <offy_name>`
* Get infomation about offy horoscope.
* Example: 
    * Input: `/ben horoscope Hoang Hiep`
    * Output: 
     `Hoang Hiep Le
        Birday : 1996-08-20
        Your sign is : Leo
        Daily horoscope on : ...`

`/ben offyskill <offy_name>`
* Get infomation about offy member skill and competencies.
* Example: 
    * Input: `/ben offyskill Hoai Linh`
    * Output: 
     `Hoai Linh Ngo
        Cluster : Caring
        Astro sign : Aquarius
        Competencies : The competency is not set
        Skills : Problem Solving (697h), Install software (35h), admin scripts (35h),`

`/ben whoskill <skill_name>`
* Give you all the offies name have this skill.
* Example: 
    * Input: `/ben whoskill php`
    * Output: 
     `You are looking for offies who have skill similar to php
        -----------------------------------------
        PHP skill: 
        Offy Name: Huu Binh Nguyen, Ngoc Thang Nguyen, Quang Hien Tran, Tan Khoa NGUYEN, Thanh Trung TO, 
        -----------------------------------------
        FuelPHP skill: 
        Offy Name: Huu Binh Nguyen, 
        -----------------------------------------`

`/ben offyage <offy_name>`
* Get infomation about offy member skill and competencies.
* Example: 
    * Input: `/ben offyage Thao Lan`
    * Output: 
     `Thao Lan NGUYEN HOANG
        Cluster : IT Crew
        Astro sign : Leo
        Created date on Dinh: 2014-06-03 04:12:14
        Offy age over: 5 year(s)`

`/ben getweather`
* You can see today weather at OffyPlex.
* Example: 
    * Input: `/ben getweather`
    * Output: 
     `Today weather: 
        -----------------------------------------
        Mostly cloudy until tomorrow afternoon.
        -----------------------------------------
        For more details: 
        https://darksky.net/forecast/10.7752,106.6704/si12/en`

`/ben getweather`
* You can see today weather at OffyPlex.
* Example: 
    * Input: `/ben getweather`
    * Output: 
     `Today weather: 
        -----------------------------------------
        Mostly cloudy until tomorrow afternoon.
        -----------------------------------------
        For more details: 
        https://darksky.net/forecast/10.7752,106.6704/si12/en`

`/ben cashin <YYYY-MM-DD>`
* Ben will tell us the total amount of Quote created on Dinh.
* Example: 
    * Input: `/ben cashin 2018-12` will show all cashin in Dec-2018 (You can also specific the day e.g: `/ben cashin 2018-12-12`)
    * Output: 
     `Name: QO2018-1204 
      Date order: 2018-12-31 
      Last update: 2018-12-31 03:31:15 
      Price:3,695.0€ 
    -----------------------------------------
    ...
    Quote sent on 2018-12: 258,405.64€`

`/ben cashout <YYYY-MM-DD>`
* Ben will tell us the total amount of PR in “to endorse” status.
* Example: 
    * Input: `/ben cashout 2018-12` will show all cashout in Dec-2018 (You can also specific the day e.g: `/ben cashout 2018-12-12`)
    * Output: 
     `Name: GS Monthly Expense- Dec 2018 (PR2018-0165) 
      Date order: 2018-12-03 
      Last update: 2018-12-04 07:24:00 
      Price:220.22€ 
      Price (VND):5,000,000đ 
    -----------------------------------------
    ...
    Expense Forecasting on 2018-12: 9,917.56€`