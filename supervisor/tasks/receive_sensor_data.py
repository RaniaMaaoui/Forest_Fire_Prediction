from celery import shared_task
from supervisor.models.data import Data
from supervisor.models.node import Node
from supervisor.fwi import FWI
from datetime import datetime

@shared_task(bind=True, name="receive_sensor_data", queue="receive_sensor")
def receive_sensor_data(self, payload):
    try:
        node = Node.objects.get(id=payload["node_id"])
        fwi_calc = FWI()

        last_data = Data.objects.filter(node=node).order_by('-published_date').first()
        FFMCPrev = last_data.ffmc if last_data else 85.0
        dmc_prev = last_data.dmc if last_data else 6.0

        ffmc = fwi_calc.FFMC(payload["temperature"], payload["humidity"], payload["wind"], payload["rain"], FFMCPrev)
        dmc = fwi_calc.DMC(payload["temperature"], payload["humidity"], payload["rain"], dmc_prev)
        isi = fwi_calc.ISI(payload["wind"], ffmc)

        data = Data.objects.create(
            temperature=payload["temperature"],
            humidity=payload["humidity"],
            pressur=payload["pressur"],
            gaz=payload["gaz"],
            wind=payload["wind"],
            rain=payload["rain"],
            detection=payload["detection"],
            ffmc=ffmc,
            dmc=dmc,
            isi=isi,
            fwi=None,
            node=node,
            published_date=datetime.now()
        )

        # Publier pour prédiction
        from supervisor.tasks.predict_fwi import predict_single_fwi
        predict_single_fwi.delay({
            "data_id": data.idData,
            "features": {
                "temperature": payload["temperature"],
                "humidity": payload["humidity"],
                "pressur": payload["pressur"],
                "gaz": payload["gaz"],
                "wind": payload["wind"],
                "rain": payload["rain"],
                "ffmc": ffmc,
                "dmc": dmc,
                "isi": isi
            }
        })

        return {"status": "saved", "data_id": data.idData}

    except Exception as e:
        raise self.retry(exc=e, countdown=10)
