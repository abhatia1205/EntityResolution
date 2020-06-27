<<<<<<< HEAD
# Quantum-Criticism

Will upload a better version of the notebook in a bit.
=======
# EntityResolution

## Description of the Project

This is my work as an intern at the Universty of San Fransisco under Prof. David Guy Brizan. I tackled the problem of entity resolution.
The task is to determine whether two tokens in natural language ( such as "Michael Jackson" and "King of Pop" ) are referring
to the same real-world entity (in the aforementioned case - the person Michael Jackson). During the internship, I created a Django
web app to help manualy label articles of text from a pipeline feeding it eral world articles. The pipeline would run named
entity recognition (finding the previously aforementioned token). I coded a web app to display these articles in such a way that
people could find the recognized entities and label them with an ID for a real world entity. To make this more conrete, lets take the
example of Donald Trump. In an article, it may refer to Trump as "Donald Trump" and "President". The web app I coded would retrun a list
of such recoginzed tokens, and let you label them with an entity id. In the previous example, both "Donal Trump" and "President"
would be labelled with, say, the id 123. 

This method of labelling data will be used to create a dataset upon which we can train an entity resolution algorithm. Just to be clear,
no Deep Learning was used in this project. Rather, it was only Django and HTML work. This being said, I did create an unsupervised 
classification algorithm for entity resolution using a word tokenization model (Word2Vec). Once sufficient data is labelled by hand,
I will try ti create a more robust algorithm.
>>>>>>> 9b67fda36eed8375ede5dd01b9b307e64b81b71c
