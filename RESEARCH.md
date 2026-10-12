# Research and Learning

## Starting point

My background and interests are more focused on infrastructure and DevOps than software development. I have used Python before at university and in some of my personal projects, including one of my projects called PoE Tracker, but I would certainly not describe myself as someone who can sit down and write everything from memory without checking anything first. I am familiar with a number of Python concepts and I can generally understand what is happening when I read code I have worked with before, however, if I have not used something for a while I will usually need to refresh myself on the syntax or look at an example before I use it again.

This is also one of the reasons why I tend to keep fairly detailed documentation for my own projects. I have found that learning or understanding something once does not necessarily mean I will remember exactly how to use it several months later. Naturally, I could search for the same information online again, but having my own documentation makes that process much easier because I already know where the information is and I know that the example is something I have previously used and understood. Once this challenge is submitted, I intend to add a small ComposeCheck section to my personal documentation as well, especially covering YAML parsing, parsing errors, pytest and the pre-commit setup.

Because of that, this challenge ended up being a mixture of things which were completely new to me and things which I had used before but needed to refresh or use in a different way. When researching, I used official Docker and Python documentation where it was useful, however I often found examples on websites such as W3Schools, GeeksforGeeks, Stack Overflow and Reddit easier to follow when I was trying to understand how a smaller piece of code worked in practice. W3Schools is something I have used since college, while GeeksforGeeks became particularly useful during this project because it often had fairly straightforward examples for some of the more specific things I was looking for.

## Defining the scope

One of the first things I needed to work out was what ComposeCheck should actually be responsible for. It would have been very easy to keep adding checks, but at the same time Docker Compose already has its own validation and trying to recreate the complete Compose specification would have made a fairly small challenge much larger than it needed to be.

Considering the brief specifically mentioned that a smaller project which is well designed and fully understood is better than a large one, I decided to focus on three problems: duplicate host ports, missing local bind-mount paths and missing environment variables. These were all problems which I could realistically see causing issues before a project is started or deployed, and some of the idea also came from issues I had run into while working on my own Docker-based projects.

With that said, I was also aware that keeping the scope small meant accepting some limitations. ComposeCheck cannot tell the user that a Compose file will definitely work, and it does not support every possible way of writing ports, volumes or environment variables. I think keeping that boundary clear was important, as otherwise it would be very easy for the project to promise more than it can actually do.

## Reading YAML from Python

I had worked with Docker Compose YAML before, but reading YAML directly from Python was new to me. The first thing I needed to understand was how a YAML file would actually look once it had been loaded into Python. I researched PyYAML and used `yaml.safe_load()` to turn the file into Python data which could then be worked through using normal dictionaries and lists.

Dictionaries, lists, loops, sets and methods such as `.split()` were not completely new to me. I had already used them in PoE Tracker, although naturally they were being used there for a different purpose. In ComposeCheck I had to refresh some of that knowledge and then apply it to the structure of a Compose file instead. Printing small parts of the parsed data and changing values was especially useful here because I could actually see what `services`, `ports`, `volumes` and `environment` looked like once Python received them.

One of the more useful mistakes happened when I intentionally misspelled a Compose key such as `ports`. I expected the parser to complain, but nothing happened. At first that felt strange, but after looking into it further it made sense: from PyYAML's perspective, `portz` is still a perfectly valid YAML key. It does not know that Docker Compose expects a particular structure.

Something similar happened when I accidentally moved `ports` inside the `environment` section while testing. The YAML still parsed successfully, but later the program failed because the data type was not what the environment checker expected. That certainly helped me understand the difference between YAML syntax being valid and a Compose file actually making sense to Docker or to my own program.

## Error handling and command-line behaviour

I had used `try` and `except` before, so exception handling itself was not new. What was newer to me was dealing with specific errors in a small command-line tool and deciding what the user should actually see when something goes wrong.

Initially, if the user supplied a file which did not exist, Python returned a full `FileNotFoundError` traceback. The traceback is useful when debugging, but from the user perspective it was far more information than was necessary. I therefore added handling for `FileNotFoundError` and later `yaml.YAMLError`, allowing ComposeCheck to return a much shorter explanation of what went wrong.

Another interesting case was an empty file or a YAML file without a top-level `services` section. Neither of these situations necessarily produces invalid YAML, so they had to be checked separately after parsing. This is where I used `isinstance()` and a key check to make sure the data had the minimum structure required by the rest of the program.

Exit codes were also a newer practical concept for me. I had used `sys` before, but not specifically `sys.exit(0)` and `sys.exit(1)` to tell another process whether something succeeded or failed. At first these values are almost invisible to the person running the command unless they check them, however later they became much more important because the pre-commit automation could use the same result to decide whether a commit should continue.

## Paths and environment variables

As for file paths, using `pathlib` in this way was new to me. The main thing I needed to understand was that a relative path inside a Compose file should be resolved relative to the Compose file itself, rather than simply wherever the user happened to launch ComposeCheck from.

Using `Path`, `.resolve()` and `compose_path.parent` made that a lot clearer. It also gave me a good example of why something which looks simple on the surface can still behave incorrectly if the context of the path is ignored.

Environment variables were more familiar because my other personal projects already use `.env` files and environment variables. However, the purpose was slightly different here. ComposeCheck was not loading environment variables for its own settings. Instead, it needed to find values such as `${DB_PASSWORD}`, extract `DB_PASSWORD`, and then check whether it was available either in the current process environment or in a `.env` file beside the Compose file.

I tested this manually in several different combinations: the value existing only in the shell, only in `.env`, in both locations and in neither location. I found this sort of testing particularly useful throughout the project because changing one small thing and seeing how the output changes usually helped me understand the behaviour better than simply reading about it.

## Refactoring and automated testing

The first working version of ComposeCheck had most of the logic in one flow. It worked, but as more checks were added it became increasingly obvious that separating the work into functions would make the code easier to follow and later easier to test.

Unit testing itself was not completely new to me because I had previously written tests for another personal project, but pytest was new in practice. I had to learn how pytest discovers tests and how fixtures such as `tmp_path` and `monkeypatch` can be used.

`tmp_path` was useful for creating temporary directories and files without filling the real project with test data. `monkeypatch` was similarly useful for environment-variable tests because it allowed me to temporarily add or remove a variable without permanently changing my own environment.

At this stage I also added:

```python
if __name__ == "__main__":
    main()
```

I had seen this structure plenty of times before, but I have to admit that I had never really needed to think much about why it exists. Once I started importing ComposeCheck functions into the test file, the reason became much clearer. Without the `main()` guard, importing the file would also run the command-line argument parsing. Moving that workflow into `main()` meant the functions could be imported and tested on their own.

In the end, I kept eight automated tests. They cover both successful and unsuccessful examples for each of the three main checks, as well as invalid YAML handling. On top of that, I manually tested cases such as missing files, missing `services` sections and the final exit codes.

## Pre-commit automation

The pre-commit hook was not part of my very first idea for the project. It came a little later when I started thinking more about how somebody would actually use the tool and how easy it is to forget a manual step.

The current hook runs the complete pytest test suite before Git accepts a commit. If the tests pass, the commit continues, and if they fail, it is blocked. I liked this addition because it took something which could easily be forgotten and made it automatic.

The first approach did not work properly, which was actually quite useful from a learning perspective. The initial configuration used `language: system`. When I tried to commit through my normal Git workflow, the hook ran but failed because Git could not find the `pytest` executable from my virtual environment.

Looking back, the configuration made sense only while assuming that the same environment would always be available when Git ran the hook. Once that assumption was proven wrong, I changed it to use a managed Python environment and explicitly included pytest and PyYAML as dependencies. I then ran the hook again and confirmed that it passed before making the actual commit.

I think this was one of the better examples from the challenge of why testing something in the way it will genuinely be used is important. On paper the first configuration looked fine, however the real workflow exposed a problem almost immediately.

## What I learned from the challenge

It would be fair to say that the biggest value of this challenge was not suddenly learning Python from the beginning. A lot of the basic building blocks were things I had encountered before, but programming is not my main discipline and I do not use them often enough to remember every piece of syntax without looking something up from time to time.

What was more useful was taking some of that existing knowledge and using it in a different context, while also learning several things which were genuinely new to me in practice, especially PyYAML, `pathlib`, pytest fixtures, command-line exit codes and pre-commit automation.

On top of that, the project reminded me why I like keeping my own technical documentation. There is a fairly large difference between understanding something while working on it and remembering exactly how to reproduce it six months later. Once ComposeCheck is submitted, I plan to add the useful parts of this project to my own documentation so that things such as YAML parsing, parsing errors and the pre-commit setup are already there the next time I need them.

Overall, my approach throughout the challenge was fairly simple: break the problem into smaller parts, look up the things I was unsure about, test them rather than assuming they worked, and make sure I understood why something was being added before moving on. It took me longer than simply copying a finished solution would have, but I believe I came away from the project understanding considerably more because of it.
