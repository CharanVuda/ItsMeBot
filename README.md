## TL;DR

Meet `ItsMe` bot, a WhatsApp chat companion powered by ChatGPT. This bot can impersonate anyone with some introduction and background. As an example, I asked the bot to impersonate 'Krish Malhotra', lead character in the book '2 States'. With the offerings from cloud providers you dont need a team of developers and an IT army to develop and maintain apps. The cost of owning this app is almost negligible. All it does is run a Python Flask app on Google Cloud Run. 

## Prerequisites to create a replica of this app

1. Creata an [OpenAI API](https://openai.com/product) account and generate an API key
2. Create a [Whatsapp Business app](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started) 
3. Create a [Google Cloud account](https://cloud.google.com/?hl=en) to run the code on `Cloud Run`
4. Deploy the code on [GCP] (https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
5. Link Cloud Run app as [webhook](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks) to your WhatsApp app 
