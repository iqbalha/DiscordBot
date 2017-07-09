import discord
from discord.ext.commands import Bot
import random
import time

client = Bot(command_prefix="<", description="Maybe")

#Load pokemon into the pokemon name list from text file
file = open("pokemonList.txt", "r")
pokNames = [item.strip() for item in file.readlines()]
file.close()
# Create names for sublists of pokemon list
pokByGen = [pokNames[:151], # gen 1
            pokNames[151:251], # gen 2
            pokNames[251:386], # gen 3
            pokNames[386:493], # gen 4
            pokNames[493:649], # gen 5
            pokNames[649:721], # gen 6
            pokNames[721:]] # gen 7

# Create a dictionary to keep track of points
scores = {}

# function that selects a random pokemon from the list or sublists
def randomPokemon(gen=0):
    pok = ""
    if gen == 0:
        pok = pokNames[random.randint(0, len(pokNames)-1)]
    elif gen <= len(pokByGen):
        gen -= 1 # convert gen to index for the list
        pok = pokByGen[gen][random.randint(0, len(pokByGen[gen])-1)]
    else:
        return ("Whoa, there is a " + str(gen)
                + "th generation now! Sorry dude, I only know up to "
                + str(len(pokByGen)) + "th gen.")
        
    return pok


# Increase the score of the given user based on time remianing
def incScore(user, time):
    if not user in scores:
        scores[user] = 0
    scores[user] += 2*time + 100
        


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command()
async def hello():
    return await client.say("Hello, user!")


@client.command()
async def bye():
    return await client.say("see ya later!")


@client.command()
async def helpList():
    return await client.say(
        "```All commands but be called with a " + client.command_prefix
        + " before the command (e.g <hello).\n"
        + "Commands with a [description] indicate that it requires an"
        + " arguement with that description. The <desc> arguments means"
        + " the argument is optional the command can be called without it.\n"
        + "These are the actions I can do for you;\n"
        + "pokid [#]: Finds pokemon with the id [#] in the pokedex.\n"
        + "randPok <#>: Randomly selects a pokemon from gen <#>.\n"
        + "start <#>: Starts a round of pictionary. <#> selects which gen.\n"
        + "guess: Starts a guessing game.\n"
        + "restart: Resets all information on the game. Such as scores.\n"
        + "scoreboard: print all the current game scores.\n"
        + "```")


# search for pokemon in the pokedex by id
@client.command()
async def pokid(idNum):
    # error check the input
    if not idNum:
        return await client.say("Invalid input: missing id paramater. (e.g. "
                                + client.command_prefix + "pokid 6)")
    if not idNum.isdigit():
        return await client.say("Bro, that argument isn't even"
                                + " a positive number.")

    # convert input to an integer to index the pokemon name list
    i = int(idNum) - 1

    if i < 0 or i >= len(pokNames):
        return await client.say("No such pokemon with that id."
                                + " Are you trying to prank me?")

    return await client.say(pokNames[i])


# Select a random pokemon based on gen
@client.command()
async def randPok(genNum=0):
    return await client.say(randomPokemon(genNum))


"""
start the pictionary game. DM the user the answer and listen for the correct
answer from the chat. (Needs DM permission on server)
"""
@client.command(pass_context=True)
async def start(ctx, gen="0"):
    # select a random pokemon from the specified gen as the answer
    answer = ""
    if gen.isdigit():
        answer = randomPokemon(int(gen))
        if len(answer) > 25: # error check the function
            return await client.say(answer)
    else:
        return await client.say("Invalid input: This command optionally takes "
                                + "a positive number as an argument. (e.g. "
                                + client.command_prefix + "start 6)")

    # DM the user the answer
    drawer = ctx.message.author
    await client.send_message(drawer, answer)
    print("answer: " + answer.lower())

    # helper function that checks user's answer
    def guess_check(m):
        if m.author == client.user:
            return False
        print("guess: " + m.content.lower())
        return m.content.lower() == answer.lower()
    
    # start timer and message time remaining every 10 seconds
    remainingTime = 0
    for i in range(100,0,-5):
        guess = await client.wait_for_message(timeout=5.0, check=guess_check)
        if guess is not None:
            remainingTime = i
            break
        await client.say(str(i-5) + " Seconds left")

    # Tell the results of the round
    if guess is None:
        return await client.say("Times up! The answer was "
                                + answer + ".")

    # increase score
    incScore(guess.author, remainingTime)
    incScore(drawer, remainingTime)
    return await client.say("Correct!")


"""
An extra guessing game where players have once chance to guess the right number
"""
@client.command()
async def guess():
    await client.say('Guess a number between 1 to 10')
    answer = random.randint(1, 10)
    
    def guess_check(m):
        return m.content.isdigit()
    
    guess = await client.wait_for_message(timeout=5.0, check=guess_check)
    
    if guess is None:
        fmt = 'Sorry, you took too long. It was {}.'
        await client.say(fmt.format(answer))
        return
    if int(guess.content) == answer:
        await client.say('You are right!')
    elif abs(int(guess.content) - answer) <= 1:
        await client.say('meh, close enough.')
    else:
        await client.say('Sorry. It is actually {}.'.format(answer))

        
#clears the scoreboard
@client.command()
async def restart():
    scores = {}
    await client.say("Scores reset")


# gives points to the player who guesssed correctly
@client.command()
async def scoreboard():
    board = ""
    for user in scores:
        if not user.nick:
            board += user.name +" has " + str(scores[user]) + " points\n"
        else:
            board += user.nick + " has " + str(scores[user]) + " points\n"
            
    if board == "":
        return await client.say("There are currently no scores")
    await client.say(board)


playerCharacters = {}
userData = {}


@client.event
async def on_message(message):

    # Place holder in case I need to add some functionlity here
    
    await client.process_commands(message)


#Load pokemon into the pokemon name list from text file
file = open("key.txt", "r")
key = file.readline().strip()
file.close()
client.run(key)
print("dissconnected")
