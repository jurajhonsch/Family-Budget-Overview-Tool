$(document).ready(() => {
    // automatic select
	$("select[value]").each(function () {
        let l = $(this).attr("value");
        if (l.length > 0) {
            $(this).val(l);
        }
    });
    
    let search = new URLSearchParams(window.location.search);

    let chart_type = search.has("chart-type") ? search.get("chart-type") : "";
    let type = search.has("type") ? search.get("type") : "";
    let category = search.has("category") ? search.get("category") : "";
    let from_date = search.has("from-date") ? search.get("from-date") : "";
    let to_date = search.has("to-date") ? search.get("to-date") : "";

    $(".apply").click(() => {
        let search = new URLSearchParams(window.location.search);
        search.set("type", $(".type option:selected").val());
        search.set("category", $(".category option:selected").val())
        search.set("from-date", $(".from-date").val());
        search.set("to-date", $(".to-date").val());
        window.location.search = search;
    });

    $.get("/chart-data?chart-type=" + chart_type + "&type=" + type + "&category=" + category + "&from-date=" + from_date + "&to-date=" + to_date).done((e) => {
        e = JSON.parse(e);

        if (e["status"] == "ok") {
            e = e["data"];
            let config;

            if (chart_type == "epoch" || chart_type == "" || chart_type == "detail") {
                config = {
                    type: e["options"]["chart_type"],
                    data: e["data"],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        color: e["options"]["theme_primary"],
                        plugins: {
                            legend: {
                                labels: {
                                    font: {
                                        size: e["options"]["font_size"],
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                grid: {
                                    display: true,
                                    color: e["options"]["theme_medium"],
                                },
                                ticks: {
                                    font: {
                                        size: e["options"]["font_size"],
                                    }
                                }
                            },
                            y: {
                                grid: {
                                    display: true,
                                    color: e["options"]["theme_medium"],
                                },
                                ticks: {
                                    font: {
                                        size: e["options"]["font_size"],
                                    }
                                }
                            },
                        }
                    }
                };
            } else {
                config = {
                    type: e["options"]["chart_type"],
                    data: e["data"],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        color: e["options"]["theme_primary"],
                        plugins: {
                            legend: {
                                labels: {
                                    font: {
                                        size: e["options"]["font_size"],
                                    }
                                }
                            }
                        }
                    }
                };
            }

            const myChart = new Chart(
                document.getElementById('myChart'),
                config
            );
        } else {
            alert("Error! " + e["description"]);
        }
    }).fail((e) => {
        e = JSON.decode(e);
        alert("Error! " + e["description"]);
    });
});