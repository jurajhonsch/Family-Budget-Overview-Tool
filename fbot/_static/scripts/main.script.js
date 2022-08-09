$.fn.isValidLength = function () {
	let logicalAnd = true;
	$(this).each(function () {
		let e = $(this);
		// trim
		e.val(e.val().trim());
		if (logicalAnd) {
			let len = e.attr("minlength");
	
			if (len) {
				if (e.val().length < len) {
					logicalAnd = false;
				}
			}
		}
	});
	return logicalAnd;
};

$.fn.isValidNumber = function (n) {
let decimals = n;
let logicalAnd = true;
$(this).each(function () {
	let e = $(this);
	if (logicalAnd) {
		if (e.val().length > 0) {
			let n = Number(e.val().trim().replace(",", ".")).toFixed(decimals);
			if (n) {
			e.val(n);
			} else {
				logicalAnd = false;
			}
		} else {
			logicalAnd = false;
		}
	}
});
return logicalAnd;
};

Date.prototype.toDateInputValue = function () {
var local = new Date(this);
local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
return local.toJSON().slice(0, 10);
};

$(document).ready(() => {
	// automatic select
	$("select[value]").each(function () {
		let l = $(this).attr("value");
		if (l.length > 0) {
			$(this).val(l);
		}
	});

	// set current date
	$(".modal-box input[name=date]").val(new Date().toDateInputValue());
	let search = new URLSearchParams(window.location.search);
	if (search.get("type") != "all") {
		$(".modal-box select[name=type]").val(search.get("type"));
	}
	if (search.get("category") != "all") {
		$(".modal-box select[name=category]").val(search.get("category"));
	}

	// nodata button
	$(".nodata").click(() => {
		$(".action-add").click();
	});

	$(".action-show-all").click(() => {
		let search = new URLSearchParams(window.location.search);
		search.set("limit", 0);
		window.location.search = search;
	});

	// epoch button
	$(".epoch").click(() => {
		let type = $(".type").val();

		if (type == "all") {
			alert("Please select type in your filter.");
			return;
		};

		let from_date = $(".from-date").val();
		let to_date = $(".to-date").val();

		window.open("/chart?chart-type=epoch&type=" + type + "&from-date=" + from_date + "&to-date=" + to_date, "_blank");
	});
	// compare button
	$(".compare").click(() => {
		let type = $(".type").val();

		if (type == "all") {
			alert("Please select type in your filter.");
			return;
		};

		let from_date = $(".from-date").val();
		let to_date = $(".to-date").val();

		window.open("/chart?chart-type=compare&type=" + type + "&from-date=" + from_date + "&to-date=" + to_date, "_blank");
	});
	// apply button
	$(".apply").click(() => {
		let search = new URLSearchParams(window.location.search);
		// LIMIT //
		search.set("limit", $(".limit").val());
		let minAmount = $(".min-amount");
		if (!minAmount.isValidNumber(2)) {
			alert("You have enter a valid number before save.");
			return;
		}
		search.set("min-amount", minAmount.val());
		let maxAmount = $(".max-amount");
		if (!maxAmount.isValidNumber(2)) {
			alert("You have enter a valid number before save.");
			return;
		}
		search.set("max-amount", maxAmount.val());
		search.set("type", $(".type").val());
		search.set("category", $(".category").val());
		search.set("from-date", $(".from-date").val());
		search.set("to-date", $(".to-date").val());
		window.location.search = search;
	});
	// clear button
	$(".clear").click(() => {
		window.location.href = window.location.href.replace(window.location.search,'');
	});
	// action after edit button clicked
	$(".action-edit").click(function () {
		let tableRow = $(this).parent().parent().parent();

		if ($(this).text() == "edit") {
			tableRow.find("input, select").removeAttr("disabled");

			$(this).text("done");
			tableRow.toggleClass("active");
		} else {
			if (!tableRow.find("input[type=number]").isValidNumber(2)) {
				alert("You have enter a valid number before save.");
				return;
			}
			if (!tableRow.find("input[type=text], input[type=date], select").isValidLength()) {
				alert("You have to fill some data before save.");
				return;
			}
			tableRow.find("input, select").attr("disabled", true);
			$.post("/update-row", {
				uuid: tableRow.find(".uuid").text(),
				name: tableRow.find("input[name=name]").val(),
				amount: tableRow.find("input[name=amount]").val(),
				type: tableRow.find("select[name=type]").val(),
				category: tableRow.find("select[name=category]").val(),
				date: tableRow.find("input[name=date]").val(),
				comment: tableRow.find("input[name=comment]").val(),
			}).done((e) => {
				e = JSON.parse(e);
				if (e.status == "ok") {
					$(this).text("edit");
					tableRow.toggleClass("active");
				} else {
					alert("Error updating row.", e.description);
				}
			}).fail((e) => {
				e = JSON.parse(e);
				alert("Error updating row.", e.description);
			});
		}
	});

	// duplicate button clicked
	$(".action-duplicate").click(function () {
		let tableRow = $(this).parent().parent().parent();

		$(".modal input[name=name]").val(tableRow.find("input[name=name]").val());
		$(".modal input[name=amount]").val(tableRow.find("input[name=amount]").val());
		$(".modal select[name=type]").val(tableRow.find("select[name=type]").val());
		$(".modal select[name=category]").val(tableRow.find("select[name=category]").val());
		$(".modal input[name=date]").val(tableRow.find("input[name=date]").val());
		$(".modal input[name=comment]").val(tableRow.find("input[name=comment]").val());

		$(".action-add").click();
	});

	// action after delete button clicked
	$(".action-delete").click(function () {
		let tableRow = $(this).parent().parent().parent();

		if (confirm("Are you sure to delete this row?")) {
			$.post("/delete-row", {
				uuid: tableRow.find(".uuid").text(),
			}).done((e) => {
				e = JSON.parse(e);
				if (e.status == "ok") {
					tableRow.remove();
				} else {
					alert("Error deleting row.", e.description);
				}
			}).fail((e) => {
				e = JSON.parse(e);
				alert("Error deleting row.", e.description);
			});
		}
	});

	// show modal after add button clicked
	$(".action-add").click(() => {
		$(".modal").toggleClass("active");
	});
	// add after add button clicked
	$(".action-close").click(() => {
		$(".modal").toggleClass("active");
	});
	$(".action-add-submit").click(() => {
		const modalBox = $(".modal-box");
		if (!$(".modal-box input[type=number]").isValidNumber(2)) {
			alert("You have enter a valid number before save.");
			return;
		}
		if (!$(".modal-box input[type=text], .modal-box input[type=date], .modal-box select").isValidLength()) {
			alert("You have to fill some data before save.");
			return;
		}
		$.post("/add-row", {
			name: modalBox.find("input[name=name]").val(),
			amount: modalBox.find("input[name=amount]").val(),
			type: modalBox.find("select[name=type]").val(),
			category: modalBox.find("select[name=category]").val(),
			date: modalBox.find("input[name=date]").val(),
			comment: modalBox.find("input[name=comment]").val(),
		}).done((e) => {
			e = JSON.parse(e);
			if (e.status == "ok") {
				window.location.reload();
			} else {
				alert("Error updating row.", e.description);
			}
			$(".modal").toggleClass("active");
		}).fail((e) => {
			e = JSON.parse(e);
			alert("Error updating row.", e.description);
		})
	});
});
