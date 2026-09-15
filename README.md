# Docker

Para el desarrollo del trabajo se decidio utiizar un programa que tenga dos paginas html y un servicio de api el cual cuente la visitas que tuvo cada pagina. El primer html sera un "Hola mundo" con una redirección al siguiente html el cual tambien va a tener una redireccion de vuelta y ademas consultar la api para mostrar la cantidad de veces que se ingreso a cada pagina y el total entre ambas.

Se utilizo la siguiente estructura en la cual de describe el uso de 2 html's (main y estadisticas), el uso de un main.py el cual contiene el codigo de una fastapi que se crea mediante el Dockerfile, un archivo txt de requerimientos para la instalacion de las bibliotecas de la api y un docker-compose que ejecutara el servicio que contiene los containers y el volumen correspondiente.

```
TP-Docker/
├── docker-compose.yaml
├── Dockerfile
├── estadisticas.html
├── main.html
├── main.py
└── requirements.txt
```

Para el caso del Dockfile se definio la siguiente estructura:

```Dockerfile
FROM python:3.11-alpine

WORKDIR /code

COPY requirements.txt /code
RUN  pip3 install -r requirements.txt

COPY main.py /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

 El Dockerfile hace un pull a la imagen de alpine de python y decide que el directorio de trabajo va a ser en /code. Dentro del directorio se copia el requirements.txt necesario para la descarga de las librerías utilizando el comando RUN. El comando COPY requiere especificar el directorio donde se copia el equipo, mientras que el RUN se ejecuta en el directorio especificado en WORKDIR. Se utiliza el comando CMD para que cuando se levante la imagen se ejecute el comando necesario para la implementacion de fastapi, el cual se habilita el puerto 8000.

Para crear la imagen mediante el Dockerfile utilizamos:
```bash
docker buildx build . -t tp-fastapi:latest
```
y para ejecutar la imagen:
```bash
docker run --name tp --rm -p 8000:8000 tp-fastapi:latest
```


Para el caso del docker-compose.yaml se definio la siguiente estructura: 

```yaml
name: tp
services:
  fastapi:
    build: .
    ports:
      - '8000:8000'
    volumes:
      - my-vol:/data/

  nginx-main:
    image: ramiroalvarez2210/nginx-main
    ports:
      - 8081:80
    volumes:
      - ./main.html:/usr/share/nginx/html/index.html:Z

  nginx-estadisticas:
    image: ramiroalvarez2210/nginx-estadisticas
    ports:
      - 8082:80
    volumes:
      - ./estadisticas.html:/usr/share/nginx/html/index.html:Z

volumes:
  my-vol:

```

El docker-compose levanta 3 contenedores que se especifican con el nombre fastapi, nginx-main y nginx-estadisticas. Para el caso de main y estadisticas realiza un pull a mi repositorio personal para utilizar las imagenes de los html's y se especifica un puerto de acceso que conecta con el puerto 80 default de nginx. Para el caso de fastapi se buildea la imagen del Dockerfile, anteriormente creado, que se encuentra en el directorio. A su vez se especifica el puerto de salida que conecta con el puerto 8000 de fastapi y un volumen detallado el cual persiste la informacion incluido dentro del directorio /data quie esta en el container de fastapi.

Para ejecutar nuestro compose utilizaremos el comando
```bash
docker compose up
```
y verificaremos que los container se ejecuten correctamente.

Podemos verificar si nuestro volumen se creo correctamente utilizando
```bash
docker volume ls
```
y luego al reiniciar o eliminar el servicio de fastapi, al levantar de nuevo podemos verificar como el volumen persiste en caso de fallas en el container.

Para el uso de la imagen main y estadisticas se utilizo un Dockerfile para cada caso y se pusheo en Docker HUB, los cuales se descargan y utilizan al levantar el compose.

```Dockerfile
FROM nginx:alpine

COPY archivo.html /nginx/
```

# Kubernetes

Para la practica de Kubernetes se reutilizaron los containers creados para la practica de Docker. Se implemento un manifiesto deployment y uno service para cada container usado (main, estadisticas y fastapi).

A continuacion el Deployment.yaml de cada servicio:


```yaml
# Deployment-main.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: main-deployment
spec:
  replicas: 4
  selector:
    matchLabels:
      app: main-pod
  template:
    metadata:
      labels:
        app: main-pod
    spec:
      containers:
        - name: main
          image: ramiroalvarez2210/nginx-main
          ports:
            - containerPort: 80

--- # Service main
apiVersion: v1
kind: Service
metadata:
  name: main-service
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 80
  selector:
    app: main-pod

--- # Deployment-estadisticas.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: estadisticas-deployment
spec:
  replicas: 4
  selector:
    matchLabels:
      app: estadisticas-pod
  template:
    metadata:
      labels:
        app: estadisticas-pod
    spec:
      containers:
        - name: estadisticas
          image: ramiroalvarez2210/nginx-estadisticas
          ports:
            - containerPort: 80

--- # Service estadisticas
apiVersion: v1
kind: Service
metadata:
  name: estadisticas-service
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 80
  selector:
    app: estadisticas-pod

--- # Deployment-fastapi.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 4
  selector:
    matchLabels:
      app: fastapi-pod
  template:
    metadata:
      labels:
        app: fastapi-pod
    spec:
      containers:
        - name: fastapi
          image: ramiroalvarez2210/tp-fastapi
          ports:
            - containerPort: 8000
          volumeMounts:
            - mountPath: /data
              name: pvc-fastapi-volume
      volumes:
      - name: pvc-fastapi-volume
        persistentVolumeClaim:
          claimName: pvc-fastapi

--- # Service fastapi
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: 8000
  selector:
    app: fastapi-pod
--- # Persistance Volume Claim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-fastapi
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Para cada deployment se especifico una cantidad de replicas igual a 4 para cada pod las cuales pueden ser redefinidas en ejecucion, un nombre especifico el cual va a ser reconocido por los servicios de cada uno cuando se levante, un nombre del container, la imagen que utilizar cada deployment y se especifico el puerto de salida en cada caso. Para el deployment de fastapi se utilizo Persistance Volume Claim de nombre pvc-fastapi para persistir la informacion de la cantidad de ingresos a las paginas en caso de que falle algun pod o nuestro servicio de api. En esta practica se decidio que el acceso de lectura y escritura sea utilizado por un unico nodo y en caso de requerir otro funcionamento se podria plantear que todos los nodos dispongan del acceso.
En el caso de los servicios se especifica el nombre del mismo, el tipo que es de ClusterIP la cual solo sera reconocida por el cluster (no hace falta definirlo ya que por default se ejecuta asi), el puerto a utilizar con el puerto del pod y el selector de cada pod.

Para ejecutar cada deployment y cada servicio podemos ejecutarlos en archivos diferentes o en uno unico, se van a crear 3 deployments y 3 servicios.

Se utiliza el siguiente comando:
```bash
kubectl apply -f NombreDeployment.yaml
```

Una vez ejecutado nuestros deployments y servicios podemos verificarlos de diferentes maneras.

Primero podemos verificar que se hayan creado los nodos correspondientes por deployment
```bash
kubectl get pods
```

Por ejemplo una vista de lo que se ve
```bash
kubectl get pods
NAME                                       READY   STATUS              RESTARTS   AGE
estadisticas-deployment-8488c84b77-42s5s   1/1     Running             0          13s
estadisticas-deployment-8488c84b77-lc8tz   1/1     Running             0          13s
estadisticas-deployment-8488c84b77-pwbzc   1/1     Running             0          13s
estadisticas-deployment-8488c84b77-rpkrt   1/1     Running             0          13s
fastapi-deployment-6f9dbf4fbb-57m9r        1/1     Running             0          9s
fastapi-deployment-6f9dbf4fbb-lf8bg        1/1     Running             0          9s
fastapi-deployment-6f9dbf4fbb-rpzh8        0/1     ContainerCreating   0          9s
fastapi-deployment-6f9dbf4fbb-sw6tf        1/1     Running             0          9s
main-deployment-88b649f9-7dhdf             1/1     Running             0          17s
main-deployment-88b649f9-dhrcw             1/1     Running             0          17s
main-deployment-88b649f9-kxmsx             1/1     Running             0          17s
main-deployment-88b649f9-zdtkf             1/1     Running             0          17s

```

Por cada service podemos consultar el tipo, la ip interna y externa  (si esta configurado) y los puertos:

```bash
kubectl get service main-service
kubectl get service estadisticas-service
kubectl get service fastapi-service
```

Para poder acceder a los servicios y por el tipo elegido (ClusterIP) se utilizo el port-forward para la prueba de los mismos. No se planteo utilizar un NodePort por el poco uso de la exposicion del puerto ni un LoadBalancer debido a ser una prueba local y sin acceso a una prueba en la nube.

```bash
kubectl port-forward service/main-service 8081:8080 &
kubectl port-forward service/estadisticas-service 8082:8080 &
kubectl port-forward service/fastapi-service 8000:8000 &
```

Luego podemos verificar los accesos con:

```bash
curl http://localhost:8081/main
curl http://localhost:8082/estadisticas
curl http://localhost:8000/stats # se utiliza para la consulta de fastapi
```

# Prueba basica

Para la prueba de nuestro deployment de servicios en kubernetes podemos utilizar los curl's mencionados anteriormente 
```bash
curl http://localhost:8081/main
curl http://localhost:8082/estadisticas
curl http://localhost:8000/stats
```
o simplemente ingresando via navegador a http://localhost:8081/main , http://localhost:8082/estadisticas y http://localhost:8000/stats .
Las respuestas esperadas para el caso de main es una pagina HTML con un "Hola mundo", para estadisticas la cantidad de accesos a las paginas y para stats (fastapi) la cantidad de acceso de las paginas, es un valor que consulta y utiliza el HTML de estadisticas.

Destacamos que el uso de port-forward siempre utiliza el mismo pod para cada caso, es algo propio de la distribucion con el comando. Si eliminamos el pod en el cual se accede, el port-forward se cierre. Por lo tanto se planteo el uso de un Ingress para la distribucion de los endpoints para cada servicio. Se utilizo el siguiente archivo .yaml.

```yaml
# Ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-service
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /main
        pathType: ImplementationSpecific
        backend:
          service:
            name: main-service
            port:
              number: 8080
      - path: /estadisticas
        pathType: ImplementationSpecific
        backend:
          service:
            name: estadisticas-service
            port:
              number: 8080
      - path: /fastapi
        pathType: ImplementationSpecific
        backend:
          service:
            name: fastapi-service
            port:
              number: 8000

```

Se especifica la ruta para cada servicio, el puerto asignad en cada paso y se especifica la implementacion especifica. Ahora podemos realizar un port-fordward para el ingress con 

```bash
kubectl port-forward ingress-service 8080:80
```

Podemos verificar el acceso a los pods con 
```bash
kubectl logs -f -l app=main-pod --prefix=true &
kubectl logs -f -l app=estadisticas-pod --prefix=true &
kubectl logs -f -l app=fastapi-pod --prefix=true &
```
y luego ingresando a las paginas o usando un comando, como por ejemplo
```bash
for i in $(seq 1 20); do curl -s http://localhost:8080/main > /dev/null; done
```
verificamos como kubernetes redistribuye el trafico y el acceso de los pods varia.

Por configuracion de las imagenes de main y estadisticas, los ruteos y asignacion de direcciones, las redirecciones de cada archivo fallan. De igual manera podemos verificar el acceso a cada servicio directamente por su definición.
