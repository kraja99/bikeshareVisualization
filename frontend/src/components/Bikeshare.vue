<template>
  <div id="Bikeshare">
    <h1>{{ msg }}</h1>
    <hr>
    <div>
      <h3>Most Popular Stations</h3>
      <p>
        These are the most popular starting and ending stations for rides. Lookup the Station ID in the location visualizer for more info on the station.
      </p>
      <div class="col1">
        <apexcharts align="center" width="700" type="bar" :options="start_station_options" :series="start_station_series"></apexcharts>
      </div>
      <div class="col2">
        <apexcharts align="center" float="right" width="700" type="bar" :options="end_station_options" :series="end_station_series"></apexcharts>
      </div>
    </div>
    <div align="center">
      <h3>Station Map</h3>
      <p>Map that shows the selected bike station and its surrounding area.</p>
      <GmapMap ref = "mapRef" :center="{lat:34.0566, lng:-118.2372}" :zoom="14" map-type-id="terrain" style="width: 500px; height: 300px">
        <GmapMarker :key="index" v-for="(m, index) in markers" :position="m.position" :clickable="false" :draggable="false"/>
      </GmapMap>
      <p></p>
      <div class="row">
        <div class="col">
        </div>
        <div class="col">
          <b-form-select v-model="selected_station" :options="station_options" class="sm" v-on:change="updateMap"/>
        </div>
        <div class="col">
        </div>
      </div>
      <hr>
    </div>
    <div>
      <h3>Average Distance Traveled</h3>
      <div class="col1">
        <h4>Average One-Way Distance: {{avg_one_way_distance}} km</h4>
        <p class="p1">
          The average one-way distance was calculated by filtering the data for all one-way rides and calculating 
          the distance between the start and end stations using their lat, long data. Averaging these distances 
          yielded the result.
        </p>
      </div>
      <div class="col2">
        <h4>Average Roundtrip Distance: {{avg_roundtrip_distance}} km</h4>
        <p class="p1">
          The average roundtrip distance was calculated by assuming an average bike-speed of 7 km/h and using the 
          given durations to find the average distance traveled. When considering the data of the one-way rides this 
          seems like an obviously flawed way to calculate this heuristic. Especially when considering factors such as 
          traffic and time actually spend riding, more data is required to make an informed estimate of the actual 
          average roundtrip distance.
        </p>
      </div>
    </div>
    <div>
      <h3>Regular Bike Share Users</h3>
      <h4>Regular Commute Users: {{commute_count}}</h4>
      <p class="p2">
        Given that there is no way to determine if each ride belongs to a specific user 
        I used the assumption that each ride is unique to count the users. Commute users 
        were considered to be users that were not Walk-up riders.
      </p>
    </div>
    <div>
      <br><br>
      <h3>Most Popular Routes</h3>
      <p>
        These are some of the most popular routes that people take when using the bikes.
      </p>
      <hr>
      <apexcharts align="center" float="right" width="800" type="bar" :options="routes_options" :series="routes_series"></apexcharts>
    </div>
    <div>
      <br>
      <h3>Check-In versus Checkout Times</h3>
      <p>
        These graphs compare the number of bikes checked in or out during a given hour.
      </p>
      <hr>
      <div class="col1">
        <apexcharts align="center" width="700" type="bar" :options="checkin_options" :series="checkin_series"></apexcharts>
      </div>
      <div class="col2">
        <apexcharts align="center" width="700" type="bar" :options="checkout_options" :series="checkout_series"></apexcharts>
      </div>
    </div>
    <div>
      <br>
      <h3>Ride Duration Comparison</h3>
      <p>
        This is a comparison of the length of rides between walk-up customers versus other customers.
      </p>
      <hr>
      <div class = "col1">
        <apexcharts align="right" width="500" type="donut" :options="walkup_options" :series="walkup_series"></apexcharts>
      </div>
      <div class = "col2">
        <apexcharts align="left" width="500" type="donut" :options="non_walkup_options" :series="non_walkup_series"></apexcharts>
      </div>
    </div>
    <div>
      <h3>Data by Seasons</h3>
      <p>I split the data into Seasons by Months (i.e. Mar, Apr, May - Spring, etc) and filtered information based on these partitions.</p>
      <h4>Average Duration(sec) By Season</h4>
      <b-table hover striped fixed :items="seasonDuration"></b-table>
      <h4>Pass Counts By Season</h4>
      <b-table hover striped fixed :items="seasonPassholderCount"></b-table>
    </div>
    <br><br><br>
    <p align="right">Made By Kiran Raja</p>
  </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts';

export default {
  name: 'Bikeshare',
  components: {
    apexcharts: VueApexCharts,
  },
  data() {
    return {
      msg: 'Bikeshare Data Visualization',
      seasonDuration: [],
      seasonPassholderCount: [],
      selected_station: null,
      station_options: [{ text: 'Select A Station', value: null }],
      markers: [{
        position: {
          lat: 34.0566,
          lng: -118.2372,
        },
      }],
      avg_one_way_distance: null,
      avg_roundtrip_distance: null,
      commute_count: null,
      routes_options: {
        chart: {
          id: 'Popular Routes',
          background: '#d3d3d3',
        },
        xaxis: {
          title: {
            text: 'Start Station ID/End Station ID',
          },
          categories: [],
        },
        yaxis: {
          title: {
            text: 'Number of Rides',
          },
        },
        theme: {
          palette: 'palette7',
        },
      },
      routes_series: [{
        name: 'Number of Rides',
        data: [],
      }],
      start_station_options: {
        chart: {
          id: 'Start Stations',
          background: '#d3d3d3',
        },
        xaxis: {
          title: {
            text: 'Start Station ID',
          },
          categories: [],
        },
        yaxis: {
          title: {
            text: 'Number of Rides',
          },
        },
        title: {
          text: 'Start Stations',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
        theme: {
          palette: 'palette5',
        },
      },
      start_station_series: [{
        name: 'Number of Rides',
        data: [],
      }],
      end_station_options: {
        chart: {
          id: 'End Stations',
          background: '#d3d3d3',
        },
        xaxis: {
          title: {
            text: 'End Station ID',
          },
          categories: [],
        },
        yaxis: {
          title: {
            text: 'Number of Rides',
          },
        },
        title: {
          text: 'End Stations',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
      },
      end_station_series: [{
        name: 'Number of Rides',
        data: [],
      }],
      walkup_options: {
        labels: ['Short (< 15 min)', 'Medium (15 - 45 min)', 'Long (> 45 min)'],
        title: {
          text: 'Walk-Up Rider',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
      },
      walkup_series: [],
      non_walkup_options: {
        labels: ['Short (< 15 min)', 'Medium (15 - 45 min)', 'Long (> 45 min)'],
        title: {
          text: 'Non Walk-Up Rider',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
      },
      non_walkup_series: [],
      checkin_options: {
        chart: {
          background: '#d3d3d3',
        },
        xaxis: {
          title: {
            text: 'Check-in Time',
          },
          categories: [],
        },
        yaxis: {
          title: {
            text: 'Number of Rides',
          },
        },
        dataLabels: {
          enabled: false,
        },
        title: {
          text: 'Check-in Count',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
        theme: {
          palette: 'palette3',
        },
      },
      checkin_series: [{
        name: 'Number of Rides',
        data: [],
      }],
      checkout_options: {
        chart: {
          background: '#d3d3d3',
        },
        dataLabels: {
          enabled: false,
        },
        xaxis: {
          title: {
            text: 'Checkout Time',
          },
          categories: [],
        },
        yaxis: {
          title: {
            text: 'Number of Rides',
          },
        },
        title: {
          text: 'Checkout Count',
          align: 'center',
          margin: 10,
          offsetX: 0,
          offsetY: 0,
          floating: false,
          style: {
            fontSize: '24px',
            color: '#2c3e50',
          },
        },
        theme: {
          palette: 'palette4',
        },
      },
      checkout_series: [{
        name: 'Number of Rides',
        data: [],
      }],
    };
  },
  created() {
    axios.get(`${process.env.ROOT_API}/initialData`)  //get data to populate charts
      .then((res) => {
        this.commute_count = res.data.RegularUsers;
        this.avg_one_way_distance = Math.round(res.data.AverageOneWayDistance * 100) / 100;
        this.avg_roundtrip_distance = Math.round(res.data.AverageRoundtripDistance * 100) / 100;
        for (let i = 0; i < res.data.MostPopularStartStation.length; i += 1) {  //populate most popular station data
          this.start_station_options.xaxis.categories.push(res.data.MostPopularStartStation[i][0]);
          this.start_station_series[0].data.push(res.data.MostPopularStartStation[i][1]);
          this.end_station_options.xaxis.categories.push(res.data.MostPopularEndStation[i][0]);
          this.end_station_series[0].data.push(res.data.MostPopularEndStation[i][1]);
        }
        for (let i = 0; i < res.data.MostPopularRoutes.length; i += 1) {  //populate most popular route data
          this.routes_series[0].data.push(res.data.MostPopularRoutes[i][2]);
          this.routes_options.xaxis.categories.push(`${res.data.MostPopularRoutes[i][0]}/${res.data.MostPopularRoutes[i][1]}`);
        }
        for (let i = 0; i < res.data.Duration_Walkup.length; i += 1) { //populate ride duration chart data
          this.walkup_series.push(res.data.Duration_Walkup[i]);
          this.non_walkup_series.push(res.data.Duration_Non_Walkup[i]);
        }
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
  },
  mounted() {
    axios.get(`${process.env.ROOT_API}/getStations`)  //get and store list of all stations
      .then((res) => {
        for (let i = 0; i < res.data.Stations.length; i += 1) {
          this.station_options.push(res.data.Stations[i]);
        }
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    axios.get(`${process.env.ROOT_API}/timeData`) //get check-in/checkout data and season data
      .then((res) => {
        this.checkin_options.xaxis.categories = [];
        for (let i = 0; i < res.data.CheckinCount.length; i += 1) {
          this.checkin_series[0].data.push(res.data.CheckinCount[i]);
          this.checkin_options.xaxis.categories.push(`${i}`);
          this.checkout_options.xaxis.categories.push(`${i}`);
          this.checkout_series[0].data.push(res.data.CheckoutCount[i]);
        }
        this.seasonDuration.push({ Spring: Math.round(res.data.DurationBySeason[0][0]),
          Summer: Math.round(res.data.DurationBySeason[0][1]),
          Fall: Math.round(res.data.DurationBySeason[0][2]),
          Winter: Math.round(res.data.DurationBySeason[0][3]) });
        this.seasonPassholderCount.push({ Passholder_Type: 'Monthly Pass',
          Spring: res.data.PassholderCountBySeason[0][0],
          Summer: res.data.PassholderCountBySeason[0][1],
          Fall: res.data.PassholderCountBySeason[0][2],
          Winter: res.data.PassholderCountBySeason[0][3] });
        this.seasonPassholderCount.push({ Passholder_Type: 'Flex Pass',
          Spring: res.data.PassholderCountBySeason[0][8],
          Summer: res.data.PassholderCountBySeason[0][9],
          Fall: res.data.PassholderCountBySeason[0][10],
          Winter: res.data.PassholderCountBySeason[0][11] });
        this.seasonPassholderCount.push({ Passholder_Type: 'Staff Annual',
          Spring: res.data.PassholderCountBySeason[0][4],
          Summer: res.data.PassholderCountBySeason[0][5],
          Fall: res.data.PassholderCountBySeason[0][6],
          Winter: res.data.PassholderCountBySeason[0][7] });
        this.seasonPassholderCount.push({ Passholder_Type: 'Walk-Up',
          Spring: res.data.PassholderCountBySeason[0][12],
          Summer: res.data.PassholderCountBySeason[0][13],
          Fall: res.data.PassholderCountBySeason[0][14],
          Winter: res.data.PassholderCountBySeason[0][15] });
        this.seasonPassholderCount.push({ Passholder_Type: 'Total',
          Spring: res.data.PassholderCountBySeason[0][0] + res.data.PassholderCountBySeason[0][4] +
            res.data.PassholderCountBySeason[0][8] + res.data.PassholderCountBySeason[0][12],
          Summer: res.data.PassholderCountBySeason[0][1] + res.data.PassholderCountBySeason[0][5] +
            res.data.PassholderCountBySeason[0][9] + res.data.PassholderCountBySeason[0][13],
          Fall: res.data.PassholderCountBySeason[0][2] + res.data.PassholderCountBySeason[0][6] +
            res.data.PassholderCountBySeason[0][10] + res.data.PassholderCountBySeason[0][14],
          Winter: res.data.PassholderCountBySeason[0][3] + res.data.PassholderCountBySeason[0][7] +
            res.data.PassholderCountBySeason[0][11] + res.data.PassholderCountBySeason[0][15] });
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
  },
  methods: {
    updateMap(event) {  //update the map whenever the user selects a station
      axios.get(`${process.env.ROOT_API}/getLatLong/${event}`)  //get the lat and long of the queried station
      .then((res) => {
        this.$refs.mapRef.$mapPromise.then((map) => { //update the maps marker and center
          map.panTo({ lat: res.data.LatLong[0], lng: res.data.LatLong[1] });
          this.markers[0].position.lat = res.data.LatLong[0];
          this.markers[0].position.lng = res.data.LatLong[1];
        });
      })
      .catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.col1 {
    float: left;
    width: 50%;
}
.col2 {
    float: left;
    width: 50%;
}
.col3 {
    float: left;
    width: 70%;
}
.col4 {
    float: left;
    width: 30%;
}

.p1 {
  margin-left: 8%;
  text-align: 'center';
  width: 80%;
}

.p2 {
  margin-left: 18%;
  text-align: 'center';
  width: 60%;
}

h4 {
  font-size: 16pt;
}

h2 {
  position: relative;
  margin-top: 20px;
}
h2.one {
  margin-top: 0;
}
h2.one:before {
  content: "";
  display: block;
  border-top: solid 1px black;
  width: 100%;
  height: 1px;
  position: absolute;
  top: 50%;
  z-index: 1;
}
h2.one span {
  background: #d3d3d3;
  padding: 0 20px;
  position: relative;
  z-index: 5;
}
</style>
