  <script>
     /* var sales_date = {{ sales_data }};
      var sold_items = {{ items }};
      var dayOfWeekLabels = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
   
     

      for(var i = 0; i < dayOfWeekLabels.length; i++) {
        document.write(dayOfWeekLabels[i] + "<br/>");
      }
   /*   var sales_data = {{sales_data|safe}};
      var dayOfWeekLabels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      
      

      for(var i = 0; i < sales_data.length; i++) {
        var sale = sales_data[i];
     
        var dayOfWeek = new Date(sale.date).getDay(); // Get the day of the week for the sale date


        for(var j = 0; j < sale.items.length; j++) {
          var product = sale.items[j].title;
          var quantity = sale.items[j].quantity;
          var price = sale.items[j].price;
      
          // Add product label to the list of product labels if it doesn't already exist
          if (productLabels.indexOf(product) === -1) {
            productLabels.push(product);
          }
      
          // Find the index of the current product in the list of product labels
          var productIndex = productLabels.indexOf(product);
      
          // If a dataset for the current product doesn't exist yet, create it
          if (!datasets[productIndex]) {
            datasets[productIndex] = {
              label: product,
              data: [0, 0, 0, 0, 0, 0, 0], // Initialize data array with 0 values for each day of the week
              backgroundColor: getRandomColor()
            };
            totalQuantities[productIndex] = 0;
            totalPrices[productIndex] = 0;
          }
      
          // Add the current quantity and price to the total quantities and prices for the current product
          totalQuantities[productIndex] += quantity;
          totalPrices[productIndex] += quantity * price;
      
          // Add the current quantity to the data array of the dataset for the current product and day of the week
          datasets[productIndex].data[dayOfWeek] += quantity;
        }
      }
      
      // Define a function to generate a random color
      function getRandomColor() {
        var letters = '0123456789ABCDEF';
        var color = '#';
        for (var i = 0; i < 6; i++) {
          color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
      }
      
      var ctx = document.getElementById('myChart2').getContext('2d');
      
      var myChart = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: dayOfWeekLabels,
              datasets: datasets 
          },
          options: {
              scales: {
                  yAxes: [{
                      ticks: {
                          beginAtZero: true
                      }
                  }]
              }
          }
      });
      */
    </script>
    

      <script>
  /*
   
        var label = {{ label|safe }};

        var sales_data = {{ sales_data|safe }};
        
        var datasets = [];
        var totalQuantities = [];
        var totalPrices = [];
        var productLabels = [];
        
        for(var i = 0; i < sales_data.length; i++) {
          
          for(var j = 0; j < sales_data[i].items.length; j++) {
            var product = sales_data[i].items[j].title;
            var quantity = sales_data[i].items[j].quantity;
            var price = sales_data[i].items[j].price;
        
            // Add product label to the list of product labels if it doesn't already exist
            if (productLabels.indexOf(product) === -1) {
              productLabels.push(product);
            }
        
            // Find the index of the current product in the list of product labels
            var productIndex = productLabels.indexOf(product);
        
            // If a dataset for the current product doesn't exist yet, create it
            if (!datasets[productIndex]) {
              datasets[productIndex] = {
                label: product,
                data: [],
                backgroundColor: getRandomColor()
              };
              totalQuantities[productIndex] = 0;
              totalPrices[productIndex] = 0;
            }
        
            // Add the current quantity and price to the total quantities and prices for the current product
            totalQuantities[productIndex] += quantity;
            totalPrices[productIndex] += quantity * price;
        
            // Add the current quantity to the data array of the dataset for the current product
            datasets[productIndex].data.push(quantity);
          }
        }
        
        // Define a function to generate a random color
        function getRandomColor() {
          var letters = '0123456789ABCDEF';
          var color = '#';
          for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
          }
          return color;
        }
        
        var ctx = document.getElementById('myChart').getContext('2d');
     
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: label,
                datasets: datasets 
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        }); */
    </script>