# 第4章:对象的组合
```
本章目的:介绍一些组合模式,这个模式能够使一个类更容易成为线程安全.并且维护这些类不会无意中破坏类的安全性保证.
```
[TOC]

### 4.1 设计线程安全类
```
使用封装技术,可以在不对整个程序进行分析的情况下,判断一个类是否线程安全.所以,推荐封装.
```
```
私有变量和共有共有静态域相比,私有变量封装性更好,在线程并发情况下,更容易保证线程安全.
```
##### 设计线程安全类的三个基本要
```
1. 找出构成对象状态的所有变量
```
```
2. 找出约束状态变量的不变性条件
```
```
3. 建立对象状态的并发访问管理策略
```
#######对象状态的分析
```
1. n个基本类型对象,其状态就是域构成的n个元组
```
```
2. 对象的域是引用,那么状态也包含引用对象的域.比如:链表的状态是所有节点对象的状态.
```
```java
@ThreadSafe
public final class Counter {
    @GuardedBy("this")
    private long value = 0;

    public synchronized long getValue() {
        return value;
    }

    public synchronized long increment() {
        if (value == Long.MAX_VALUE)
            throw new IllegalStateException("counter overflow");
        return ++value;
    }
}
```
Note:
```
状态只有value变量来控制.
```
```
3. 同步策略:定义了如何在不违背对象不变条件或后验条件的情况下对其状态的访问操作进行协同.
```

#####4.1.1 收集同步需求
```
并发情况下,需要保证类的不变性条件和后验条件.比如:不可变条件,Counter类中,value必须大于0.
后验条件:下一个状态依赖于当前状态,当前值是17,下一个值是18.
```
```
由于不变性条件以及后验条件在状态及状态转换上施加各种约束,因此需要额外的同步与封装.
```

#####4.1.2 依赖状态的操作
```
类的不变性条件和后验条件约束了在对象上有哪些状态和状态转换是有效的.但还有一种先验条件
```
```
先验条件:依赖状态的操作,比如:队列移除某个元素时,需要队列不空.并发程序需要考虑先验条件.
```
```
想实现某个等待先验条件为真时才执行的操作,Java提供类库(阻塞队列[Blocking Queue]或信号量或其他的同步工具)
```

#####4.1.3 状态的所有权
```
C++中对所有权特别强调:把一个对象传递个某个方法,必须考虑是否传递对象的所有权,短期所有权还是长期.
```
```
很多时候,所有权和封装是相互关联的.比如:某个对象被封装到一个类中,则该类具有这个对象的所有权,需要对这个对象的并发访问负责.
```
```
容器类通常表现出一种"所有权分离"的形式.也就是说,容器类拥有其自身的状态,而客户代码具有容器中各个对象的状态.
```

###4.2 实例封闭
```
封装提供一种实例封闭机制,简化线程安全类的实现过程.
```
```
将数据封装在对象内部,可以将数据的访问限制在对象的方法上,更容易确保线程安全.
但要注意的一点是:被封闭的对象不能逸出
```
#####对象封闭
```
1. 对象可以封闭在类的一个实例上(作为类的私有成员)
```
```
2. 对象可以封闭在某个作用域内(作为一个局部变量)
```
```
3. 封闭在一个线程内(比如:将对象从一个方法传递到另一个方法内,必须是同一个线程)
```
- 举例:

```java
@ThreadSafe
public class PersonSet {
    @GuardedBy("this")
    private final Set<Person> mySet = new HashSet<Person>();

    public synchronized void addPerson(Person p) {
        mySet.add(p);
    }

    public synchronized boolean containsPerson(Person p) {
        return mySet.contains(p);
    }
}
```
Note:
```
HashMap并不是线程安全的,但是mySet被封闭到PersonSet类中,唯一的访问路径被内置锁保护,所以这是一个线程安全的类.
```
```
需要提醒:如果Person是可变的,那么mySet将Person逸出时,还需要额外的同步.
```
#####装饰器
```
Java内库中提供很多的线程封闭示例,唯一的用途就是将非线程安全的类转化为线程安全类.
比如:Collections.synchronizedList为ArrayList提供线程安全装饰器.
```
```
装饰器只是接口中每个方法实现为同步方法,并将调用请求转发到底层的容器上.
```

##### 4.2.1 Java监视器模式
```
Java监视器模式会把对象的所有可变状态都封装起来,并由对象自己的内置锁来保护.比如:Counter类
```
```
第11章将介绍如何通过细粒度的加锁策略来提高可伸缩性.Java监视器模式主要优势:简单.
```
```
锁可以是内置锁,也可以是私有锁
```
- 举例:
```java
public class PrivateLock {
    private final Object myLock = new Object();
    @GuardedBy("myLock")
    Widget widget;

    void someMethod() {
        synchronized (myLock) {
            // Access or modify the state of widget
        }
    }
}
```
Note:
```
与使用内置锁相比,私有的锁对象可以保证客户代码无法得到锁,但客户代码可以通过公有方法访问锁.
```

##### 4.2.2 示例:车辆追踪
```
下面举例,关于java监视器模式的示例:一个用于调度车辆的"车辆追踪器"
```
```
每台车都有一String的对象作为标识,并且拥有相应的坐标(x,y).
会有一个视图线程用于显示车辆位置,多个更新操作线程执行更新.
```
```
视图线程与执行更新操作的线程将并发的访问数据模型,因此需要并发.
```
```java
public class MonitorVehicleTracker {
    @GuardedBy("this")
    private final Map<String, MutablePoint> locations;

    public MonitorVehicleTracker(Map<String, MutablePoint> locations) {
        this.locations = deepCopy(locations);
    }

    public synchronized Map<String, MutablePoint> getLocations() {
        return deepCopy(locations);
    }

    public synchronized MutablePoint getLocation(String id) {
        MutablePoint loc = locations.get(id);
        return loc == null ? null : new MutablePoint(loc);
    }

    public synchronized void setLocation(String id, int x, int y) {
        MutablePoint loc = locations.get(id);
        if (loc == null)
            throw new IllegalArgumentException("No such ID: " + id);
        loc.x = x;
        loc.y = y;
    }

    private static Map<String, MutablePoint> deepCopy(Map<String, MutablePoint> m) {
        Map<String, MutablePoint> result = new HashMap<String, MutablePoint>();

        for (String id : m.keySet())
            result.put(id, new MutablePoint(m.get(id)));

        return Collections.unmodifiableMap(result);
    }
}

@NotThreadSafe
public class MutablePoint {
    public int x, y;

    public MutablePoint() {
        x = 0;
        y = 0;
    }

    public MutablePoint(MutablePoint p) {
        this.x = p.x;
        this.y = p.y;
    }
}
```
Note:
```
1. 尽管MutablePoint是线程安全,但是MutablePoint类封装在MonitorVehicleTracker类中
```
```
2. deepCopy方法,为了保证线程安全,必须返回一个Collections.unmodifiableMap(map),而且,Map中的对象必须是复制的一份.二者,缺一不可.
```
```
3. 实现的方式是通过返回客户代码之前复制可变的数据来维持线程安全.但是,如果车辆容器非常大的情况下可能有极大的性能问题
性能问题解释:dedpCopy是从一个synchronized方法中调用,因此执行时间较长的复制操作.当有大量车辆需要追踪时,锁保证了每次只有一个线程访问.
```

### 4.3 线程安全性的委托
```
Java监视器非常适合:1.从头开始构建一个类; 2.将多个非线程安全的类组合为一个类.
```
```
但如果类中各个组件都已经是线程安全的,我们可能需要视情况而定,看是否需要再增加一个额外的线程安全层.
```
##### 4.3.1 示例:基于委托的车辆追踪器
```
上面的例子是一个基于Java监视器的车辆追踪器.
下面将构造一个委托给线程安全类的车辆追踪器.
```
####### 使用不可变类Point代替MutablePoint类
```java
@Immutable
public class Point {
    public final int x, y;

    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
```
Note:
```
Point类是不可变类,所以肯定是线程安全的,可以被自由的共享与发布.
```
####### DelegatingVehicleTraceker
```java
@ThreadSafe
public class DelegatingVehicleTracker {
    private final ConcurrentMap<String, Point> locations;
    private final Map<String, Point> unmodifiableMap;

    public DelegatingVehicleTracker(Map<String, Point> points) {
        locations = new ConcurrentHashMap<String, Point>(points);
        unmodifiableMap = Collections.unmodifiableMap(locations);
    }

    public Map<String, Point> getLocations() {
        return unmodifiableMap;
    }

    public Point getLocation(String id) {
        return locations.get(id);
    }

    public void setLocation(String id, int x, int y) {
        if (locations.replace(id, new Point(x, y)) == null)
            throw new IllegalArgumentException("invalid vehicle name: " + id);
    }
}
```
Note:
```
DelegatingVehicleTracker类使用ConcurrentHashMap类,保证locations并发操作.
```
```
Collections.unmodifiableMap(mapObject),相当于locations的快照.必须使用,如果直接返回locations,那么Map中对象引用可能被修改.
```
#######需要说明一点
```
方法getLocations()返回的是一个具体对象,线程A调用getLocations()后,线程B更新某个Point,那么线程A是可以看到的,如果不想看大,使用下面的代码
```
```java
    public Map<String, Point> getLocationsAsStatic() {
        return Collections.unmodifiableMap(
                new HashMap<String, Point>(locations));
    }
```

##### 4.3.2 独立的状态变量
```
只要变量是彼此独立的,就可以将线程安全性委托给多个状态变量.
```
#######举例
```
下面将给出例子:VisualComponent是一个图形组件,允许客户程序注册监控鼠标和键盘等事件监听器.
鼠标和键盘监听器都是独立的,所以可以将线程安全性委托给两个线程安全的监听列表
```
```java
public class VisualComponent {
    private final List<KeyListener> keyListeners
            = new CopyOnWriteArrayList<KeyListener>();
    private final List<MouseListener> mouseListeners
            = new CopyOnWriteArrayList<MouseListener>();

    public void addKeyListener(KeyListener listener) {
        keyListeners.add(listener);
    }

    public void addMouseListener(MouseListener listener) {
        mouseListeners.add(listener);
    }

    public void removeKeyListener(KeyListener listener) {
        keyListeners.remove(listener);
    }

    public void removeMouseListener(MouseListener listener) {
        mouseListeners.remove(listener);
    }
}
```
Note:
```
CopyOnWriteArrayList类用来保存各个监听器雷彪.它是一个线程安全链表,特别适用于管理监听器列表(5.2.3)
```
```
两个链表是独立的,同时具有线程安全,所以上面类也是线程安全的
```

##### 4.3.3 当委托失效时
```
开发中,大多数组合对象不会像VisualComponent类那样简单,它们的状态与状态之间存在不变性条件.
比如:第一个值要小于第二个数值-- lower <= upper
```
```java
public class NumberRange {
    // INVARIANT: lower <= upper
    private final AtomicInteger lower = new AtomicInteger(0);
    private final AtomicInteger upper = new AtomicInteger(0);

    public void setLower(int i) {
        // Warning -- unsafe check-then-act
        if (i > upper.get())
            throw new IllegalArgumentException("can't set lower to " + i + " > upper");
        lower.set(i);
    }

    public void setUpper(int i) {
        // Warning -- unsafe check-then-act
        if (i < lower.get())
            throw new IllegalArgumentException("can't set upper to " + i + " < lower");
        upper.set(i);
    }

    public boolean isInRange(int i) {
        return (i >= lower.get() && i <= upper.get());
    }
}
```
Note:
```
NumberRange非线程安全.setLower()和setUpper()都是先检查后执行.
假如:线程A调用setLower(5),线程B调用setUpper(4),在某种执行顺序下,可能通过检查,存入无效状态.
```
```
某些类含有符合操作,可能仅靠委托并不足以实现线程安全性.需要提供自己的加锁机制.
```
```
如果一个类是由多个独立且线程安全的状态变量组成,并且在所有操作中都不包含无效状态转换,
那么可以将线程安全性委托给底层的状态变量.
```

##### 4.3.4 发布底层的状态变量
```
什么条件下才可以发布这些变量,从而使其他类能修改它们?
答案是：取决于类中对这些变量施加了哪些不变性条件．
```
```
如果一个状态变量是线程安全的,并且没有任何不变性条件来约束它的值,
在变量的操作上也不存在任何不允许的状态转换,那么就可以安全地发布这个变量.
比如:VisualComponent类中的keyListeners,mouseListeners就可以.
```
##### 4.3.5 示例:发布状态的车辆追踪器.
```
再举一个例子:使用可变且线程安全的Point类,并在这个版本中发布底层的可变状态.
```
```java
@ThreadSafe
public class SafePoint {
    @GuardedBy("this")
    private int x, y;

    private SafePoint(int[] a) {
        this(a[0], a[1]);
    }

    public SafePoint(SafePoint p) {
        this(p.get());
    }

    public SafePoint(int x, int y) {
        this.set(x, y);
    }

    public synchronized int[] get() {
        return new int[]{x, y};
    }

    public synchronized void set(int x, int y) {
        this.x = x;
        this.y = y;
    }
}
```
Note:
```
不能分别提供x和y的get方法.这样会产生非线程安全.
```
```java
@ThreadSafe
public class PublishingVehicleTracker {
    private final Map<String, SafePoint> locations;
    private final Map<String, SafePoint> unmodifiableMap;

    public PublishingVehicleTracker(Map<String, SafePoint> locations) {
        this.locations = new ConcurrentHashMap<String, SafePoint>(locations);
        this.unmodifiableMap = Collections.unmodifiableMap(this.locations);
    }

    public Map<String, SafePoint> getLocations() {
        return unmodifiableMap;
    }

    public SafePoint getLocation(String id) {
        return locations.get(id);
    }

    public void setLocation(String id, int x, int y) {
        if (!locations.containsKey(id))
            throw new IllegalArgumentException("invalid vehicle name: " + id);
        locations.get(id).set(x, y);
    }
}
```
Note:
```
允许修改SafePointer,但修改是可以保证原子性的.所以没有问题.
```

### 4.4 在现有的线程安全类中添加功能
```
Java类库中包含了许多有用的"基础模块",应该优先选择重用现有的类.
但往往现有的类只能支持大部分的操作,此时就需要在不破坏线程安全性的情况下添加一个新的操作.
```
##### 举例
```
一种方法是扩展需要添加功能的类,比如vector
```
```
"若没有则添加"是一个非常典型的需要线程保护的操作.
```
```java
@ThreadSafe
public class BetterVector<E> extends Vector<E> {
    // When extending a serializable class, you should redefine serialVersionUID
    static final long serialVersionUID = -3963416950630760754L;

    public synchronized boolean putIfAbsent(E x) {
        boolean absent = !contains(x);
        if (absent)
            add(x);
        return absent;
    }
}
```
Note:
```
这种方法非常脆弱,因为同步策略分布到不同的文件维护,当底层发生修改,使用不通的锁,那就gg了.
```

##### 4.4.1 客户端加锁机制
```
扩展类的功能,但并不是扩展类本身,而是将扩展代码放入一个辅助类中.
```
```
下面将举例"若没有则添加"操作的辅助类.但代码是错误的
```
```java
@NotThreadSafe
class BadListHelper<E> {
    public List<E> list = Collections.synchronizedList(new ArrayList<E>());

    public synchronized boolean putIfAbsent(E x) {
        boolean absent = !list.contains(x);
        if (absent)
            list.add(x);
        return absent;
    }
}
```
Note:
```
因为锁的对象并不是BadListHelper<E>,使用不通的锁,所以synchronized是没有用处的.
但是上面举例的类BetterVector是有效的,因为存在锁具有对象性.
```
```java
@ThreadSafe
class GoodListHelper<E> {
    public List<E> list = Collections.synchronizedList(new ArrayList<E>());

    public boolean putIfAbsent(E x) {
        synchronized (list) {
            boolean absent = !list.contains(x);
            if (absent)
                list.add(x);
            return absent;
        }
    }
}
```
Note:
```
这个可以保证线程安全.但是在客户端加锁,是非常脆弱的,因为类C的加锁代码放到与C完全无关的类中.
使用时,非常不友好,难以维护.
```

##### 4.4.2 组合

















