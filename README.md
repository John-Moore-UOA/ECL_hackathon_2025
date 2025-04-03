# Empathic Computing Lab Hackathon 2025

- [Empathic Computing Website](https://empathiccomputing.org/)
- [Empathic Computing Lab](https://www.auckland.ac.nz/en/abi/our-research/research-groups-themes/empathic-computing-laboratory.html)

![image](https://github.com/user-attachments/assets/eca5ebcb-f372-482a-be22-b1bff889e8d7)

## Team
- John Moore
- Tamil Selvan Gunasekaran
- Carl Tang
  
## Challenge
Solve a problem that ABI (Auckland Uni Bioengineering Institute) faces.

## Our Problem
New team members / researchers feel disconnected from the rest of the ABI. 

## Our Solution
- A coffee coaster that activates a network wide alert when one user takes their cup to the coffee room.
- The backend system will send messages to the different coasters, based on the user's similarities of hobbies etc.
- Users can modify thier hobbies / activities
- Algorithm will select the 5 closest users based on a random interest selected by the user
- Break time between when it calls to any single coaster of one hour

## Backend

### Python schedule_person_picker
- Goal: Find users with similar interests

#### Run through:
- Select a user at random
- Select random interest
- Select users with direct edge to interest
- If not enough users are interested in the same thing, resort to a global similarity search using Word2Vec similarity
![image](https://github.com/user-attachments/assets/4ab0e019-f7bd-49a8-ba16-c5d4cecd591d)
![image](https://github.com/user-attachments/assets/e40e041c-f777-427d-a0e5-6efe10953264)
![image](https://github.com/user-attachments/assets/08e5f11f-5fa5-43b7-b0d3-39967271ebb5)
![image](https://github.com/user-attachments/assets/d75f7103-d435-4b17-b5c3-49c051ca193c)
![image](https://github.com/user-attachments/assets/66bab61b-a2c1-4ae9-b4ef-f617615b84d2)

# output
```
Schduler started. Running every 5 minutes...
Fetching users with similar interest to user: 5
Users that have similar interests: ['1']
```

## Frontend

![image](https://github.com/user-attachments/assets/d439f9ec-1884-4ead-b074-bd4f10a5d050)
![image](https://github.com/user-attachments/assets/3c2f35b4-de88-460d-bc38-560d78cef291)







