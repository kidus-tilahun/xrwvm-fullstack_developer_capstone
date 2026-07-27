const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(express.json());

const reviews_data = JSON.parse(fs.readFileSync('data/reviews.json', 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync('data/dealerships.json', 'utf8'));

const Reviews = require('./review');
const Dealerships = require('./dealership');

// Connect to local MongoDB container (127.0.0.1) and seed only after successful connection
mongoose.connect("mongodb://127.0.0.1:27017/dealershipsDB")
  .then(async () => {
    console.log('Connected to MongoDB successfully!');
    try {
      await Reviews.deleteMany({});
      await Dealerships.deleteMany({});

      // Safely extract arrays whether flat or nested
      const reviewsToInsert = Array.isArray(reviews_data) ? reviews_data : (reviews_data.reviews || []);
      const dealersToInsert = Array.isArray(dealerships_data) ? dealerships_data : (dealerships_data.dealerships || []);

      await Reviews.insertMany(reviewsToInsert);
      await Dealerships.insertMany(dealersToInsert);

      console.log(`Database populated! Inserted ${reviewsToInsert.length} reviews and ${dealersToInsert.length} dealers.`);
    } catch (err) {
      console.error('Error populating database:', err);
    }
  })
  .catch((err) => console.error('MongoDB connection error:', err));
// 1. Fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    const documents = await Reviews.find();
    res.status(200).json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

// 2. Fetch reviews by dealer ID
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const dealerIdParam = req.params.id;
    const documents = await Reviews.find({
      $or: [
        { dealership: parseInt(dealerIdParam) },
        { dealership: String(dealerIdParam) }
      ]
    });
    res.status(200).json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching reviews for dealer' });
  }
});

// 3. Fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.status(200).json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

// 4. Fetch dealerships by state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const documents = await Dealerships.find({ state: req.params.state });
    res.status(200).json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealerships by state' });
  }
});

// 5. Fetch dealership by ID
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const document = await Dealerships.findOne({ id: req.params.id });
    if (!document) {
      return res.status(404).json({ message: 'Dealer not found' });
    }
    res.status(200).json(document);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching dealer by ID' });
  }
});

// 6. Insert review
app.post('/insert_review', async (req, res) => {
  try {
    const data = req.body;
    const documents = await Reviews.find().sort({ id: -1 });
    let new_id = documents.length > 0 ? documents[0]['id'] + 1 : 1;

    const review = new Reviews({
      "id": new_id,
      "name": data['name'],
      "dealership": data['dealership'],
      "review": data['review'],
      "purchase": data['purchase'],
      "purchase_date": data['purchase_date'],
      "car_make": data['car_make'],
      "car_model": data['car_model'],
      "car_year": data['car_year']
    });

    const savedReview = await review.save();
    res.status(200).json(savedReview);
  } catch (error) {
    res.status(500).json({ error: 'Error inserting review' });
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on http://localhost:${port}`);
});