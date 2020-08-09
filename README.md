mail2task
========

A Pythonic Email assistant which converts your emails into a `Task' on your favorite Task management Application.
(Only Todoist supported at this point)

Motivation
----------
My dread point-and-click interaction with applications including task-managers drives me towards CLI - but don't live there. I am not very organized and slip on even adding the tasks regularly - much less marking them complete. I also want something that can remind me on the go - with a right swipe on what's next, or my phone, or whatever device I chose to. But, yet - supports automation and prioritization. After years of jumping between solutions, Taskwarrior has come as the closest to the system that would work for me. But, I am not that organized to maintain my tasks there.

One thing I always do is interact with my emails - I'm good at sending emails - and without leaving the application. Hence, came the notion for this utility -- as a necessity to create tasks from Emails - something I use all the time. The fundamental ability to convert an email into task offers endless possibilities - for more on that, please see the wishlist at the end.

Installation
------------
1. There is no pip based installation (for now). Currently, I plan to clone the library to a cloud VM and CRONTAB my assistant to update my TODOIST.

2. The project uses `EZGMAIL` (https://github.com/asweigart/ezgmail) and `PYTODOIST` (https://github.com/Garee/pytodoist) as the fundamental libraries you need to have. Accordingly, you will need to setup the API access - as per the documentation for gmail, TODOIST respectively. Please refer the the respective projects and the service providers (GMAIL, TODOIST) for more details.

3. After setting up the tokens for accessing GMAIL, TODOIST - the application should just work. Please review `main.py` to ensure.

Syntax of EMAILs
----------------
Currently, I use a rather awkward JSON like subject line declaration. The syntax isn't pretty - so the usage is integrated with ESPANSO (https://github.com/federico-terzi/espanso) to have custom templates which make the awkward declarations a breeze.

    ^ is used as the separator instead of " - because I thought this is the least used character for subject lines. 

Suggestions/better ways to declare the subject are most welcome. The current syntax is:
    
    {^project^:^NAME_OF_PROJECT^, ^due_in^:^TIME_OFFSET^, ^priority^:^0--4^,^title^:^DEFINE_THE_TASK^}

TIME_OFFSET can be in hours, days, weeks, months, or years (H,D,W,M,Y respectively - case insensitive) 
    
    E.g. +1w : After 1 week, +8d : After 8 days, +2h - After 2 hours, and so on.
    These declarations can not be combined (+1D2H not allowed)

Priority: 0 - Not important, 1 - Low, 2 - Normal, 3 - High, 4 - Very high

Espanso Templates
-----------------
Espanso is such an excellent tool, with so many great features. Using two of its very useful features - Clipboard extension, and Passive mode (https://espanso.org/docs/).

1. (Type and) Cut the Description to be converted into the task. Espanso can wrap the clipboard data into a predefined format - :todoparse/$|$,+2d,2,{{clipboard}}/. Upon cutting the description - pressing `:todo' will invoke the said format before JSON.

    - trigger: ":todo"
      replace: ":todoparse/$|$,+2d,2,{{clipboard}}/"
      vars:
        - name: "clipboard"
          type: "clipboard"

2. Updating the details of the task: Project name, changing the due date (default - +2d) and priority (2 - Normal). Then you need to select the entire line and press your PASSIVE_TRIGGER key twice to get the template: 
    {^project^:^NAME_OF_PROJECT^, ^due_in^:^TIME_OFFSET^, ^priority^:^0--4^,^title^:^DEFINE_THE_TASK^}

The respective espanso setting is below:

    - trigger: ":todoparse"
      replace: "{^project^:^$0$^, ^due_in^:^$1$^, ^priority^:^$2$^,^title^:^$3$^}"
      passive_only: true

3. At this point, you just send an email to the email id being monitored. The CRONTAB agent (or other update mechanism) will filter through all the unread emails (and can mark them as unread) and then update the tasks based on the emails with pre-defined subject line.

Suggestions/improvements are welcome to make this simpler. I have some ideas in the wishlist that would be neat to find their way into this utility.


Disclaimer: Use of `espanso' is highly recommended. 


Vision
------
This application aspires to decouple the design choices between the available platforms of choice, and the declarations that are most intuitive to the end user. I say this realizing that the current iteration of subject line interpretation is biased on my declaration. But, that should evolve over time.

    Note: I'm not a seasoned programmer. Your support is much appreciated to improve/expand the code and the architecture.

Structure
---------
In the traditional pythonic way, the application is an orchestra of different agents specializing in specific tasks. I currently have `4` broaders types of classes representing the specific functionalities.
- Email interpreter - reads the emails
- Generic Tasks - Defines the generic task structure
- Task interpreter - Converts the read email to a task with due dates, etc
- Manager - Agent using the specific APIs to interact with the application of your choice to manage your tasks.

Ideally, the application will grow to support many more platforms - including Taskwarrior - which has so much to learn from. Same for email interpreters. Accordingly, the task interpreter will evolve to effortlessly bridge the differences between the two, and broader/common properties can be percolated using generic tasks.


Wishlist
--------
- Defining a host of tasks based on custom templates also included in the project. I plan to add another field `template' to the JSON-like declaration. If non-empty, it can invoke a series of sequence of tasks - defined under the given project (Taskwarrior is a big inspiration). I see a template declaration system for TODOIST on github, but haven't used it.

- Support for Taskwarrior - Use of UUIDs, conditional priority, and a host of other features makes Taskwarrior the ideal database. It would be great to use taskwarrior's structure as the database for cloud instance. This would be particularly helpful when expanding functionalities on queries, editing tasks, or when multiple projects may have similar sub-project titles (e.g. Meetings, etc).

- NLP based contextual tagging - I wasn't able to find a reliable context aware filtering to make the subject line more intutive. This would remove the intricacies of the subject line declaration.

- Multiple tasks in one email - Subject may indicate that this email contains multiple tasks. The body of the email can then be interpreted as such.

- Ability to set reminders. Python interfaces of Taskwarrior can invoke these conditionally - and send reminders via emails. All the more reason to integrate Taskwarrior.

- Support for sub-tasks (like in TODO-ist which are also listed as tasks - but with a parent)

- Add support for other popular task management applications.

- Adding notes (like when forwarding a received email as a task)


Contribute
----------
Please check out to me on https://risjain.github.io/ or via a PR - for improvements or suggestions. 
