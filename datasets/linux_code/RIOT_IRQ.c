#include <linux/interrupt.h>
#include <linux/module.h>
MODULE_LICENSE("GPL");
static int irq=11;    
static irqreturn_t irq_handler(int data, void *dev_id)
{
    printk("the data is :%d\n", data);      
    printk("in the interrupt handler function\n");
    return IRQ_NONE;
}
static int __init enable_disable_irq_init(void)
{
    int result=0;
    printk("into enable_disable_irq_init\n");
    result=request_irq(irq, irq_handler, IRQF_DISABLED, "A_New_Device", NULL);
    disable_irq(irq);
    enable_irq(irq); 
    printk("the result of the request_irq is: %d\n", result);    
    printk("out enable_disable_irq_init\n");
    return 0;
}
static void __exit enable_disable_irq_exit(void)
{
    free_irq(irq, NULL);    
    printk("Goodbye enable_disable_irq\n");
    return;
}
