import json
import os
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer


basedir = os.path.abspath(os.path.dirname(__file__))


class LangandCodeBot(object):

    def __init__(self, bot_name, basedir=basedir):
        self.slash = '/'
        self.basedir = basedir
        self.path_to_massanger = basedir+self.slash+'inbox'
        self.sub_directories = [ f.name for f in os.scandir(self.path_to_massanger) if f.is_dir() ]

        self.bot = ChatBot(bot_name,
            logic_adapters=[
                'chatterbot.logic.MathematicalEvaluation',
                {'import_path': 'chatterbot.logic.BestMatch',
                'default_response': 'I am sorry, but I do not understand.',
                'maximum_similarity_threshold': 0.90},
                'chatterbot.logic.BestMatch'
            ],
            preprocessors=[
                'chatterbot.preprocessors.clean_whitespace',
                'chatterbot.preprocessors.convert_to_ascii'
                ]
            )

        self.list_trainer = ListTrainer(self.bot)


    def get_massanger_files(self, directory):
        return sorted([f.name for f in os.scandir(
            self.path_to_massanger+self.slash+directory) if f.is_file() ])


    def load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)


    def parse_json(self, file_obj):
        previous_participant = None
        previous_message = None
        chat = []
        for m in reversed(file_obj['messages']):
            if 'content' in m:
                if previous_participant == m['sender_name'] and previous_message != None:
                    previous_message = previous_message +". "+ m['content']
                else:
                    if previous_message != None:
                        chat.append(previous_message)
                    previous_participant = m['sender_name']
                    previous_message = m['content']
            pass
        return chat


    def train_massanger_corpus(self):
        for d in self.sub_directories:
            print("Loading directory", d)
            for f in reversed(self.get_massanger_files(d)):
                print("Processing file", f)
                chat = self.parse_json(
                    self.load_json(self.path_to_massanger+self.slash+d+self.slash+f
                    )
                )
                print("Finished processing file", f)
                trainer = self.list_trainer
                print("Training with dataset {} ".format(f))
                trainer.train(chat)
                print("Trained with dataset {} ".format(f))


    def console_run_bot(self):

        print('Type something to begin...')

        # The following loop will execute each time the user enters input
        while True:
            try:
                user_input = input()

                bot_response = self.bot.get_response(user_input)

                print(bot_response)

            # Press ctrl-c or ctrl-d on the keyboard to exit
            except (KeyboardInterrupt, EOFError, SystemExit):
                break


bot = LangandCodeBot("Adam")
bot.train_massanger_corpus()
bot.console_run_bot()
