		$('.filterSelect').selectize({
		    dropdownParent: 'body',
		    allowEmptyOption: true
		});
		$('#select-school').selectize({
		    dropdownParent: 'body',
		    persist: false,
		    options: [],
		    create: false,
		    labelField: "short_desc",
		    valueField: "id",
		    searchField: "short_desc",
		    load: function(query, callback) {
		        if (!query.length) return callback();
		        var city = $("#select-city").val(),
		            supervision = $("#select-supervision").val();
		        var filterData = {
		            q: query
		        };
		        if (city != "הכל")
		            filterData.city = city;
		        if (supervision != "הכל")
		            filterData.supervision = supervision;
		        $.ajax({
		            url: BASE_API_URL,
		            type: 'GET',
		            data: filterData,
		            beforeSend: function() {
		                $("#loading-indicator").show();
		            },
		            error: function() {
		                callback();
		            },
		            success: function(res) {
		                $("#loading-indicator").hide();
		                callback(res);
		            }
		        });
		    }
		});
		var schoolFilterSelectize = $('#select-school')[0].selectize;
		var clearSchoolFilter = function() {
		    console.log("Clear!");
		    schoolFilterSelectize.clearOptions();
		    schoolFilterSelectize.renderCache = {};
		};
		$('#select-supervision')[0].selectize.on('item_add', clearSchoolFilter);
		$('#select-city')[0].selectize.on('item_add', clearSchoolFilter);


		function isNumber(n) {
		    return !isNaN(parseFloat(n)) && isFinite(n);
		}

		function getMaxPriceText(maxPriceValue, paidValue) {
		    // The api can return us 3 types of responses - either an actual price(a number), zero(which means the school can't charge for this field) or null(which means there isn't a limit to how much the school can charge for this field)
		    if(maxPriceValue === 0){
		    	return "בית הספר שלך לא רשאי לגבות תשלום על סעיף זה בכיתה זו או בכלל!"
		    }
		    if(paidValue > maxPriceValue)
		    	return maxPriceValue;
		    else
		    	return "-";
		}

		function paymentClauseToRow(paymentClauseType, paymentClause) {
		    var row = $("<tr>");
		    // Not always there - can be null
		    var maxPrice = paymentClause.max_price;
		    var price = paymentClause.price;
		    var clauseTypeColumn = $("<td>").text(paymentClauseType);
		    var clauseNameColumn = $("<td>").text(paymentClause.name);
		    var clausePriceColumn = $("<td>").text(price);
		    var clauseMaxPriceColumn = $("<td>").text(getMaxPriceText(maxPrice, price));
		    row.append(clauseNameColumn, clauseTypeColumn, clausePriceColumn, clauseMaxPriceColumn);
		    return row;
		}
		function getTalanHours(talanClauses){
			var talanHours = 0;
			talanClauses.forEach(function(talanClause){
				var price = talanClause.price,
		        maxPrice = talanClause.max_price, priceForHour = talanClause.price_for_one;
			    talanHours += Math.floor(price / priceForHour);
			});
			return talanHours;
		}
		function getTalanSummaryText(payment, row){
		var talanHours = getTalanHours(payment.clauses);
		var summaryText = 'את/ה משלמ/ת על ' + talanHours + ' שעות תל"ן';
		return summaryText;
		}
		function getPriceSummaryText(payment, row) {
			var price = payment.price,
		        maxPrice = payment.max_price;
		    var paymentType = payment.type;
		    console.log(paymentType, TALAN_TYPE);
		    if (paymentType === TALAN_TYPE) {
		        return getTalanSummaryText(payment, row);
		    }
		    var priceSummaryText =  "את/ה משלמ/ת " + price + "₪";
		    var priceDifference = Math.abs(maxPrice - price);
		    if (price > maxPrice) {
		        row.addClass("danger");
		        priceSummaryText += " והמחיר המקסימלי הינו " + maxPrice + "₪. את/ה משלמ/ת " + priceDifference +"₪ יותר!";
		    }
		    return priceSummaryText;
		}

		function createPaymentTypeSummary(payment) {
		    if (payment.clauses.length === 0) {
		        // No payments, so no summary row.
		        return;
		    }
		    var row = $("<tr>");
		    var nameColumn = $("<td>").text("סה\"\כ " + payment.type);
		    var priceSummaryText = getPriceSummaryText(payment, row);
		    // 3 is the number of other columns except the name.
		    var priceSummaryColumn = $("<td>").text(priceSummaryText).attr("colspan", 3);
		    row.append(nameColumn, priceSummaryColumn);
		    return row;
		}
		$("#submit").click(function() {
		    var selectedSchoolId = schoolFilterSelectize.getValue();
		    if (isNumber(selectedSchoolId)) {
		        var errorMessageElem = $("#errorMessage");
		        getSchoolPayments(selectedSchoolId, function(payments) {
		                errorMessageElem.hide();
		                $("#paymentsTable").show();
		                $("#explanationText").show();
		                payments.forEach(function(payment) {
		                    var paymentClauses = payment.clauses;
		                    // bind is a little hack to pass payment type to the mapping function.
		                    var paymentClausesRows = paymentClauses.map(paymentClauseToRow.bind(null, payment.type));
		                    var paymentTypeSummaryRow = createPaymentTypeSummary(payment);
		                    var paymentRows = paymentClausesRows;
		                    paymentRows.push(paymentTypeSummaryRow);
		                    $("#paymentsBody").append(paymentRows);
		                });
		            },
		            function(statusCode, errorMessage) {
		                var errorMessage;
		                if (errorMessage === "class not found") {
		                    errorMessage = "כיתה זו לא קיימת בבית ספר זה.";
		                } else if (errorMessage == "school not found") {
		                    errorMessage = "בית ספר זה אינו קיים";
		                } else if (errorMessage == "payments not found") {
		                    errorMessage = "חוזר התשלומים של המוסד לא אושר ע\"י הפיקוח. המוסד אינו רשאי לגבות תשלום.";
		                }
		                console.dir(errorMessage);
		                errorMessageElem.text(errorMessage);
		                errorMessageElem.show();
		                $("#paymentsTable").hide();
		                $("#explanationText").show();
		            });
		    }
		});

		function getSchoolPayments(schoolId, successCallback, errorCallback) {
		    var className = $('#select-class')[0].selectize.getValue();
		    // Clear payments table
		    $("#paymentsTable").hide();
		    $("#paymentsBody").empty();
		    $.ajax({
		        url: BASE_API_URL + schoolId + '/payments',
		        type: 'GET',
		        data: {
		            class: className
		        },
		        success: function(res) {
		            successCallback(res);
		        },
		        error: function(res) {
		            errorCallback(res.status, res.responseJSON.message);
		        }
		    });
		}