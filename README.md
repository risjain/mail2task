mail2task
========

A Pythonic Email assistant which converts your emails into a `Task` on your favorite Task management Application.
(Only Todoist supported at this point)

Motivation
----------
I am not very organized and occasionally slip even on adding the tasks regularly - much less marking them complete. 

My dread for point-and-click interaction with applications including task-managers drives me towards CLI - but I don't live there. But, for usability, it is best to have a friendly applicaiton that can remind me on the go - with a right swipe on what's next, or my phone, or whatever device I chose to. But, yet - supports automation and prioritization. After years of jumping between solutions, Taskwarrior has come as the closest to the system that would work for me. Alas! I am not that organized to maintain my tasks there.

One thing I always do is email - and without leaving the application. Hence, came the notion for this utility -- as a necessity to create tasks from Emails - something I use all the time. The fundamental ability to convert an email into task offers endless possibilities - for more on that, please see the wishlist at the end.

Installation
------------
1. There is no pip based installation (for now). Currently, I plan to clone the library to a cloud VM and CRONTAB my assistant to update my TODOIST.

2. The project uses `EZGMAIL` (https://github.com/asweigart/ezgmail) and `PYTODOIST` (https://github.com/Garee/pytodoist) as the fundamental libraries you need to have. Accordingly, you will need to setup the API access - as per the documentation for gmail, TODOIST respectively. Please refer the the respective projects and the service providers (GMAIL, TODOIST) for more details.

3. After setting up the tokens for accessing GMAIL, TODOIST - the application should just work. Please review `main.py` to ensure.

Syntax of EMAILs
----------------
Tasks can be added via email into your task manager in three ways:
```
1) Single tasks (defined in the subject) 
2) Multiple tasks in the email body (1 per line) - Subject says "add_all"
3) Based on a template (or multiple sub-folders with their own tasks) - Subject says "add_toml"
```

*Single Tasks*

The default task addition method uses an unusual JSON like subject line declaration. The syntax isn't pretty - so the usage is integrated with ESPANSO (https://github.com/federico-terzi/espanso) to have custom templates which make the awkward declarations a breeze.

    ^ is used as the separator instead of " - because I thought this is the least used character for subject lines. 

Suggestions/better ways to declare the subject are most welcome. The current syntax is:
    
    {^project^:^NAME_OF_PROJECT^, ^due_in^:^TIME_OFFSET^, ^priority^:^0--4^,^title^:^DEFINE_THE_TASK^}

TIME_OFFSET can be in hours, days, weeks, months, or years (H,D,W,M,Y respectively - case insensitive) 
    
    E.g. +1w : After 1 week, +8d : After 8 days, +2h - After 2 hours, and so on.
    These declarations can not be combined (+1D2H not allowed)

Priority: 0 - Not important, 1 - Low, 2 - Normal, 3 - High, 4 - Very high

*Multiple Tasks in the email body*
The structure stays the same as (1) - except that the intent of adding multiple tasks is declared in the email subject (case-sensitive) - "add_all" without quotes.

*Based on a template*

Suppose we have an upcoming event with multiple tasks, sub-projects, their own tasks, etc. Using the default one/multiple task option will be too cumbersome. Therefore, now there is an option to define the nested heirarchy (not indent sensitive) as an email. /Writing a template might be just as cumbersome as point-and-click" and we will use different templates to largely eliminate that (Template to create templates ^_^)

```
[[proj_list]]                       <---- Declares the project/sub-project (Sub-projects will be proj_list.proj_list, and so on
Parent = ^Test^		            <---- Name of the parent project (in the Root of the task manager)
project = ^Sub-Proj 1^              <---- Name of the project to be created (A sub-project folder will be created -- for all the tasks in proj_list.task)
 
[[proj_list.task]]		
due_in = ^+4D^
priority = ^2^
title = ^Task in Sub-Proj 1^        <---- Description of the sub-task under the newly created folder

[[proj_list.proj_list]]
project = ^Sub-sub-Proj 1^          <---- Sub-folder created under Sub-proj 1
 
[[proj_list.proj_list.task]]        <---- Task under sub-sub-proj 1
due_in = ^+4h^
Priority = ^2^
title = ^Task in Sub-sub-proj 1^



[[proj_list]]                       <---- Declares another project under the specified root folder
Parent = ^Test^		            <---- Name of the parent project (in the Root of the task manager)
project = ^Sub-Proj 2^              <---- Name of the project to be created (A sub-project folder will be created -- for all the tasks in proj_list.task)
 
[[proj_list.task]]		
due_in = ^+4D^
priority = ^2^
title = ^Task in Sub-Proj 2^        <---- Description of the sub-task under the newly created folder - Sub-proj 2

```

```
Note: The routine doesn't handle case-sensitive arguments. This is one of the primary reason to encourage using snippets and other tools to handle the redundancy.
```

Espanso Templates (Optional, Highly Recommended)
-----------------
Espanso is such an excellent tool, with so many great features. Using two of its very useful features - Clipboard extension, and Passive mode (https://espanso.org/docs/).

1. (Type and) Cut the Description to be converted into the task. Espanso can wrap the clipboard data into a predefined format - :todoparse/$|$,+2d,2,{{clipboard}}/. Upon cutting the description - pressing `:todo` will invoke the said format before JSON:
```
    - trigger: ":todo"
      replace: ":todoparse/$|$,+2d,2,{{clipboard}}/"
      vars:
        - name: "clipboard"
          type: "clipboard"
```
2. Updating the details of the task: Project name, changing the due date (default - +2d) and priority (2 - Normal). Then you need to select the entire line and press your PASSIVE_TRIGGER key twice to get the template: 
    {^project^:^NAME_OF_PROJECT^, ^due_in^:^TIME_OFFSET^, ^priority^:^0--4^,^title^:^DEFINE_THE_TASK^}

The respective espanso setting is below:

```
    - trigger: ":todoparse"
      replace: "{^project^:^$0$^, ^due_in^:^$1$^, ^priority^:^$2$^,^title^:^$3$^}"
      passive_only: true
```

3. At this point, you just send an email to the email id being monitored. The CRONTAB agent (or other update mechanism) will filter through all the unread emails (and can mark them as unread) and then update the tasks based on the emails with pre-defined subject line.

4. Templates (TOML) - TOML is used to offer a visually readable, and easy to parse input format for the tool. The template format was defined in previous section. Here the corresponding espanso templates are presented (if you choose to use these).
```
    - trigger: ":topr" # To project
      replace: ":totomlpr/$|$,{{clipboard}}/" # To TOML Project
      vars:
        - name: "clipboard"
          type: "clipboard"

    - trigger: ":tost" # To sub-task
      replace: ":totomlst/{{clipboard}},$|$+2d,2/" # To TOML Sub-task
      vars:
        - name: "clipboard"
          type: "clipboard"
```
```
  - trigger: ":totomlpr" # To sub-task
    replace: "[[proj_list]]\nparent = ^$0$^\nproject = ^$1$^\n" # To TOML Task
    passive_only: true

  - trigger: ":totomlst" # To sub-task
    replace: "[[proj_list.task]]\ntitle = ^$0$^\ndue_in = ^$1$^\npriority = ^$2$^\n" # To TOML Task
    passive_only: true
```

Disclaimer: Use of `espanso` is highly recommended but not mandatory. 
```
Suggestions/improvements are welcome to make this simpler. I have some ideas in the wishlist that would be neat to find their way into this utility.
```

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
- (WIP - 1st Iteration done) Multiple tasks in one email - Subject may indicate that this email contains multiple tasks. The body of the email can then be interpreted as such.

- (WIP - 1st iteration working) Defining a host of tasks based on custom templates also included in the project. I plan to add another field `template` to the JSON-like declaration. If non-empty, it can invoke a series of sequence of tasks - defined under the given project (Taskwarrior is a big inspiration). I see a template declaration system for TODOIST on github, but haven't used it.

- Support for Taskwarrior - Use of UUIDs, conditional priority, and a host of other features makes Taskwarrior the ideal database. It would be great to use taskwarrior's structure as the database for cloud instance. This would be particularly helpful when expanding functionalities on queries, editing tasks, or when multiple projects may have similar sub-project titles (e.g. Meetings, etc).

- NLP based contextual tagging - I wasn't able to find a reliable context aware filtering to make the subject line more intutive. This would remove the intricacies of the subject line declaration.

- Ability to set reminders. Python interfaces of Taskwarrior can invoke these conditionally - and send reminders via emails. All the more reason to integrate Taskwarrior.

- Support for sub-tasks (like in TODO-ist which are also listed as tasks - but with a parent)

- Add support for other popular task management applications.

- Adding notes (like when forwarding a received email as a task)


Contribute
----------
Please check out to me on https://risjain.github.io/ or via a PR - for improvements or suggestions. 
