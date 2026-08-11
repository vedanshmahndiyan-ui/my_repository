let creatures = [];
let numCreatures = 8;

function setup() {
    createCanvas(640, 240);
    pixelDensity(1);
    
    for (let i = 0; i < numCreatures; i++) {
        creatures.push(new Creature(i));
    }
}

function draw() {
    background(10, 20, 30, 25);
    
    for (let creature of creatures) {
        creature.update();
        creature.display();
    }
}

function mousePressed() {
    for (let creature of creatures) {
        creature.reset();
    }
}

class Creature {
    constructor(id) {
        this.id = id;
        this.pos = createVector(random(width), random(height));
        this.vel = createVector(0, 0);
        this.acc = createVector(0, 0);
        this.maxSpeed = random(1.5, 4);
        this.maxForce = random(0.05, 0.2);
        this.wanderStrength = random(0.5, 2);
        this.noiseScale = random(0.01, 0.05);
        this.t = random(1000);
        this.size = random(3, 8);
        this.color = this.generateColor();
        this.trail = [];
        this.maxTrail = random(5, 15);
        this.jitterAmount = random(0.1, 0.5);
        this.flowInfluence = random(0.3, 0.8);
        this.personality = this.generatePersonality();
    }
    
    generatePersonality() {
        let types = ['erratic', 'smooth', 'darting', 'drifting'];
        return types[this.id % types.length];
    }
    
    generateColor() {
        let hue = random(360);
        return color(`hsb(${hue}, 80, 90)`);
    }
    
    reset() {
        this.pos = createVector(random(width), random(height));
        this.vel = createVector(0, 0);
        this.acc = createVector(0, 0);
        this.trail = [];
        this.t = random(1000);
    }
    
    update() {
        this.t += 0.01;
        
        let wanderForce = this.wander();
        let noiseForce = this.noiseFlow();
        let jitterForce = this.jitter();
        
        wanderForce.mult(1 - this.flowInfluence);
        noiseForce.mult(this.flowInfluence);
        
        this.applyForce(wanderForce);
        this.applyForce(noiseForce);
        this.applyForce(jitterForce);
        
        this.vel.add(this.acc);
        this.vel.limit(this.maxSpeed);
        this.pos.add(this.vel);
        this.acc.mult(0);
        
        this.trail.push(this.pos.copy());
        if (this.trail.length > this.maxTrail) {
            this.trail.shift();
        }
        
        if (this.pos.x < 0) this.pos.x = width;
        if (this.pos.x > width) this.pos.x = 0;
        if (this.pos.y < 0) this.pos.y = height;
        if (this.pos.y > height) this.pos.y = 0;
    }
    
    wander() {
        let wanderR = 25;
        let wanderD = 80;
        let change = 0.3;
        
        let theta = random(TWO_PI);
        let circlePos = this.vel.copy();
        circlePos.normalize();
        circlePos.mult(wanderD);
        circlePos.add(this.pos);
        
        let h = createVector(wanderR * cos(theta), wanderR * sin(theta));
        let target = p5.Vector.add(circlePos, h);
        let steer = p5.Vector.sub(target, this.pos);
        steer.limit(this.maxForce * this.wanderStrength);
        
        return steer;
    }
    
    noiseFlow() {
        let angle = noise(this.pos.x * this.noiseScale, this.pos.y * this.noiseScale, this.t) * TWO_PI * 2;
        let force = p5.Vector.fromAngle(angle);
        force.mult(this.maxForce * 0.5);
        return force;
    }
    
    jitter() {
        let jitter = createVector(random(-1, 1), random(-1, 1));
        jitter.mult(this.jitterAmount * this.maxForce);
        return jitter;
    }
    
    applyForce(force) {
        this.acc.add(force);
    }
    
    display() {
        noStroke();
        
        if (this.trail.length > 1) {
            for (let i = 0; i < this.trail.length - 1; i++) {
                let alpha = map(i, 0, this.trail.length, 0, 150);
                let weight = map(i, 0, this.trail.length, 0.5, this.size * 0.3);
                stroke(red(this.color), green(this.color), blue(this.color), alpha);
                strokeWeight(weight);
                line(this.trail[i].x, this.trail[i].y, this.trail[i + 1].x, this.trail[i + 1].y);
            }
        }
        
        stroke(0);
        strokeWeight(1);
        fill(this.color);
        
        if (this.personality === 'erratic') {
            push();
            translate(this.pos.x, this.pos.y);
            rotate(this.vel.heading());
            triangle(this.size, 0, -this.size * 0.5, this.size * 0.5, -this.size * 0.5, -this.size * 0.5);
            pop();
        } else if (this.personality === 'smooth') {
            ellipse(this.pos.x, this.pos.y, this.size * 2, this.size);
        } else if (this.personality === 'darting') {
            push();
            translate(this.pos.x, this.pos.y);
            rotate(this.vel.heading());
            triangle(this.size * 1.5, 0, -this.size, this.size * 0.3, -this.size, -this.size * 0.3);
            pop();
        } else {
            ellipse(this.pos.x, this.pos.y, this.size * 1.5, this.size * 1.5);
        }
        
        fill(255, 200);
        noStroke();
        ellipse(this.pos.x + this.vel.x * 2, this.pos.y + this.vel.y * 2, 2, 2);
    }
}
